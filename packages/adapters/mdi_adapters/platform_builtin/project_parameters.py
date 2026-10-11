"""Controlled numeric operations; no expression evaluator or arbitrary IO."""
from __future__ import annotations

import csv
import hashlib
import io
import math
import re
from dataclasses import dataclass, field
from decimal import Decimal, localcontext
from typing import Any

from jsonschema import Draft202012Validator

from mdi_artifact_core import ArtifactPayload, stable_json_dumps, validate_viewer_scene
from mdi_schemas import Artifact, ArtifactType
from mdi_tool_registry.project_parameters import PARAMETER_TOOLS, SI_REFERENCE_SOURCE, parameter_tool_schema, si_reference

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError


@dataclass
class ParameterResult:
    title: str
    columns: list[str]
    rows: list[dict[str, Any]]
    facts: list[dict[str, Any]]
    method: str
    limitations: list[str]
    resolved: dict[str, Any]
    figure: dict[str, Any] | None = None
    model: Any = None
    origin: str = "USER_PARAMETERS"
    details: dict[str, Any] = field(default_factory=dict)


def parameter_hash(params: dict[str, Any]) -> str:
    return hashlib.sha256(stable_json_dumps(params).encode("utf-8")).hexdigest()


def _fact(predicate: str, value: Any, unit: str | None = None, subject: str = "summary") -> dict[str, Any]:
    return {"predicate": predicate, "value": value, "unit": unit, "subject": subject}


def _finite(value: Any) -> float:
    if type(value) not in (int, float) or not math.isfinite(value) or abs(value) > 1e100:
        raise ValueError("数值超出支持范围，请缩小参数或输入范围。")
    return float(value)


def validate_parameters(tool_id: str, params: dict[str, Any]) -> None:
    if not Draft202012Validator(parameter_tool_schema(tool_id)).is_valid(params):
        raise ValueError("输入不符合此工具的参数范围，请检查数值、单位与必填参数。")
    # JSON Schema does not by itself reject NaN on every numeric constraint.
    def check(value: Any) -> None:
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("输入需要有限数值，不能包含 NaN 或无穷大。")
        if isinstance(value, dict):
            for item in value.values():
                check(item)
        if isinstance(value, list):
            for item in value:
                check(item)
    check(params)


def _convert(params: dict[str, Any]) -> ParameterResult:
    reference = si_reference()
    units = {unit: (dimension, spec) for dimension, item in reference["definitions"].items() for unit, spec in item["units"].items()}
    source, target = params["from_unit"], params["to_unit"]
    dimension, before = units[source]
    target_dimension, after = units[target]
    difference = params.get("quantity", "value") == "temperature_difference"
    if dimension != target_dimension or (difference and dimension != "temperature"):
        raise ValueError("这两个单位不属于同一物理量；温差选项仅适用于温度单位。")
    rows, facts = [], []
    with localcontext() as context:
        context.prec = 50
        source_offset = Decimal(0 if difference else before.get("offset", "0"))
        target_offset = Decimal(0 if difference else after.get("offset", "0"))
        for index, value in enumerate(params["values"]):
            base = Decimal(str(value)) * Decimal(before["scale"]) + source_offset
            if dimension == "temperature" and not difference and base < 0:
                raise ValueError("绝对温度不能低于 0 K；若输入是温差，请明确使用温差换算。")
            output = _finite(float((base - target_offset) / Decimal(after["scale"])))
            rows.append({"原数值": value, "原单位": source, "换算结果": output, "目标单位": target})
            facts.extend([_fact("calculation.input_value", value, source, f"row:{index}"),
                          _fact("calculation.output_value", output, target, f"row:{index}")])
    facts.extend([_fact("calculation.quantity", "温差" if difference else reference["definitions"][dimension]["label"]),
        _fact("calculation.conversion_factor", float(Decimal(before["scale"]) / Decimal(after["scale"]))),
        _fact("calculation.conversion_offset", float((source_offset - target_offset) / Decimal(after["scale"])), target),
        _fact("reference.version", SI_REFERENCE_SOURCE.version)])
    return ParameterResult(f"单位换算 · {source} → {target}", list(rows[0]), rows, facts,
        reference["definitions"][dimension]["definition"], ["单位换算基于输入数值，不验证样品性质或测量精度。"],
        {**params, "quantity": params.get("quantity", "value")})


def _function_spec(raw: dict[str, Any]) -> tuple[dict[str, Any], str]:
    kind = raw["kind"]
    if kind == "polynomial":
        spec = dict(raw)
        formula = " + ".join(f"({coefficient:g})" + (f"·x^{power}" if power else "")
                             for power, coefficient in enumerate(raw["coefficients"]) if coefficient)
        return spec, formula or "0"
    spec = {"kind": kind, "amplitude": raw.get("amplitude", 1), "offset": raw.get("offset", 0)}
    if kind == "gaussian":
        spec.update(center=raw.get("center", 0), sigma=raw.get("sigma", 1))
        return spec, f"{spec['amplitude']:g}·exp(-0.5·((x-({spec['center']:g}))/{spec['sigma']:g})^2)+({spec['offset']:g})"
    spec.update(rate=raw.get("rate", 1), phase=raw.get("phase", 0))
    name = {"sine": "sin", "cosine": "cos", "exponential": "exp", "logarithm": "ln"}[kind]
    return spec, f"{spec['amplitude']:g}·{name}({spec['rate']:g}·x+({spec['phase']:g}))+({spec['offset']:g})"


def _function_value(spec: dict[str, Any], x: float) -> float:
    kind = spec["kind"]
    if kind == "polynomial":
        value = 0.0
        for coefficient in reversed(spec["coefficients"]):
            value = value * x + coefficient
        return _finite(value)
    if kind == "gaussian":
        argument = -0.5 * ((x - spec["center"]) / spec["sigma"]) ** 2
        value = math.exp(argument)
    else:
        argument = spec["rate"] * x + spec["phase"]
        if kind == "logarithm" and argument <= 0:
            raise ValueError("自然对数的整个绘图区间都需要正的自变量，请调整区间或函数参数。")
        if kind in {"sine", "cosine"} and abs(argument) > 1e12:
            raise ValueError("三角函数的自变量过大，请缩小区间或频率参数。")
        if kind == "exponential" and argument > 200:
            raise ValueError("指数函数超出可展示数值范围，请缩小区间或指数参数。")
        value = {"sine": math.sin, "cosine": math.cos, "exponential": math.exp, "logarithm": math.log}[kind](argument)
    return _finite(spec["amplitude"] * value + spec["offset"])


def _curves(params: dict[str, Any]) -> ParameterResult:
    start, end, count = params["x_min"], params["x_max"], int(params.get("point_count", 201))
    if end <= start:
        raise ValueError("绘图区间终点必须大于起点。")
    xs = [start + (end - start) * index / (count - 1) for index in range(count)]
    xs[0], xs[-1] = start, end
    if any(right <= left for left, right in zip(xs, xs[1:])):
        raise ValueError("区间太小，当前数值精度无法保留互不重复的采样点。")
    rows, specs, traces = [{"x": x} for x in xs], [], []
    facts = [_fact("calculation.point_count", count, "count"), _fact("calculation.x_min", start), _fact("calculation.x_max", end)]
    columns = ["x"]
    for index, raw in enumerate(params["functions"]):
        spec, formula = _function_spec(raw)
        name = f"曲线 {chr(65 + index)}"
        ys = [_function_value(spec, x) for x in xs]
        for row, y in zip(rows, ys):
            row[name] = y
        specs.append(spec)
        columns.append(name)
        traces.append({"type": "scatter", "mode": "lines", "name": name, "x": xs, "y": ys})
        facts.extend([_fact("calculation.function", "y = " + formula, subject=name),
            _fact("calculation.sampled_min", min(ys), subject=name), _fact("calculation.sampled_max", max(ys), subject=name),
            _fact("calculation.start_value", ys[0], subject=name), _fact("calculation.end_value", ys[-1], subject=name)])
        for key, value in spec.items():
            for offset, number in enumerate(value if isinstance(value, list) else [value]):
                if type(number) in (float, int):
                    facts.append(_fact(f"calculation.parameter.{key}", number, subject=f"{name}:{key}:{offset}"))
    return ParameterResult("函数曲线", columns, rows, facts,
        "在闭区间等距采样注册函数；多项式系数按常数项到最高次排列，三角函数采用弧度，自然对数以 e 为底。",
        ["曲线连接有限采样点；最小值和最大值仅指这些采样点，不代表解析极值。", "这些函数是参数化数学模型，不代表样品测量或拟合结果。"],
        {**params, "point_count": count, "functions": specs},
        {"data": traces, "layout": {"title": "函数曲线", "xaxis": {"title": "x", "range": [start, end]}, "yaxis": {"title": "y"}}})


def formula_counts(formula: str) -> dict[str, float]:
    from mdi_tool_registry.element_reference import element_reference
    symbols = {item["symbol"] for item in element_reference()["records"]}
    tokens = re.findall(r"[A-Z][a-z]?|(?:\d+(?:\.\d+)?|\.\d+)|[()]", formula)
    if "".join(tokens) != formula or not tokens:
        raise ValueError("请使用不含电荷、同位素或结晶水分隔符的化学式，例如 Fe2O3 或 Ca(OH)2。")
    position = 0

    def amount() -> Decimal:
        nonlocal position
        if position < len(tokens) and re.fullmatch(r"\d+(?:\.\d+)?|\.\d+", tokens[position]):
            value = Decimal(tokens[position])
            position += 1
            if not 0 < value <= 1e6:
                raise ValueError("化学计量数必须大于零且不超过支持范围。")
            return value
        return Decimal(1)

    def group(depth: int = 0) -> dict[str, Decimal]:
        nonlocal position
        if depth > 4:
            raise ValueError("化学式括号层级超出支持范围。")
        counts: dict[str, Decimal] = {}
        while position < len(tokens) and tokens[position] != ")":
            token = tokens[position]
            position += 1
            if token == "(":
                values = group(depth + 1)
                if position >= len(tokens) or tokens[position] != ")" or not values:
                    raise ValueError("化学式括号不匹配或为空。")
                position += 1
            elif token in symbols:
                values = {token: Decimal(1)}
            else:
                raise ValueError("化学式包含未知元素或不支持的计量写法。")
            multiplier = amount()
            for symbol, value in values.items():
                counts[symbol] = counts.get(symbol, Decimal(0)) + value * multiplier
                if counts[symbol] > 1e6:
                    raise ValueError("化学计量数超出支持范围。")
        return counts

    counts = group()
    if position != len(tokens) or not 1 <= len(counts) <= 16:
        raise ValueError("化学式括号不匹配或元素种类超出支持范围。")
    return {symbol: float(value) for symbol, value in counts.items()}


def _composition(params: dict[str, Any]) -> ParameterResult:
    formula = params["formula"]
    counts = formula_counts(formula)
    total = math.fsum(counts.values())
    rows = [{"元素": symbol, "化学计量数": count, "原子分数": count / total, "原子百分比": count / total * 100} for symbol, count in counts.items()]
    facts = [_fact("composition.formula", formula), _fact("composition.total_stoichiometry", total, "count")]
    for row in rows:
        subject = row["元素"]
        facts.extend([_fact("composition.element", subject, subject=subject), _fact("composition.stoichiometry", row["化学计量数"], "count", subject),
            _fact("composition.atomic_fraction", row["原子分数"], "fraction", subject), _fact("composition.atomic_percent", row["原子百分比"], "%", subject)])
    figure = {"data": [{"type": "bar", "x": list(counts), "y": [row["原子百分比"] for row in rows]}],
              "layout": {"title": f"{formula} · 原子组成", "xaxis": {"title": "元素", "type": "category"}, "yaxis": {"title": "原子百分比（%）", "range": [0, 100]}}}
    return ParameterResult(f"{formula} · 化学式组成", list(rows[0]), rows, facts,
        "解析元素及括号中的化学计量数；原子分数为该元素计量数除以全部元素计量数之和。",
        ["这是输入化学式的化学计量组成，不代表样品实测组成、质量分数或晶体结构。"], dict(params), figure)


_NUMBER = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")


def parse_inline_table(raw: str) -> tuple[list[str], list[list[float]]]:
    lines = raw.strip().splitlines()
    if not 3 <= len(lines) <= 131 or any(not line.strip() for line in lines):
        raise ValueError("请提供带表头的 2–128 行连续数值表格。")
    if "|" in lines[0]:
        fields = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
        if len(fields) > 1 and all(re.fullmatch(r":?-{3,}:?", cell) for cell in fields[1]):
            fields.pop(1)
    else:
        delimiter = "\t" if "\t" in lines[0] else ","
        fields = [[cell.strip() for cell in row] for row in csv.reader(io.StringIO(raw.strip()), delimiter=delimiter, strict=True)]
    headers, values = fields[0], fields[1:]
    if (not 2 <= len(headers) <= 4 or len(set(headers)) != len(headers)
            or any(not header or len(header) > 80 or re.search(r"[<>{}`\\\r\n]", header) for header in headers)
            or not 2 <= len(values) <= 128):
        raise ValueError("需要 2–4 个不同列名与 2–128 行数值，不支持空列名或可执行标记。")
    rows = []
    for row in values:
        if len(row) != len(headers) or any(not _NUMBER.fullmatch(cell) for cell in row):
            raise ValueError("各行必须具有相同列数与有效数值；缺值、公式或文本不会被静默删除。")
        rows.append([_finite(float(cell)) for cell in row])
    return headers, rows


def _header_unit(header: str) -> str | None:
    found = re.search(r"[（(\[]\s*([^()\[\]（）]+)\s*[）)\]]$", header)
    if not found:
        return None
    unit = found[1].strip()
    aliases = {"Å": "angstrom", "Å": "angstrom", "μm": "um", "µm": "um", "μs": "us", "µs": "us", "°C": "degC"}
    canonical = aliases.get(unit, unit)
    known = {key for item in si_reference()["definitions"].values() for key in item["units"]}
    return canonical if canonical in known else None


def _inline(params: dict[str, Any]) -> ParameterResult:
    headers, matrix = parse_inline_table(params["data_text"])
    x, ys = int(params.get("x_column", 0)), [int(value) for value in params.get("y_columns", [1])]
    if x >= len(headers) or any(y >= len(headers) or y == x for y in ys):
        raise ValueError("横轴和纵轴需要指向表格中不同的有效列。")
    style = params.get("style", "line")
    rows = [dict(zip(headers, row)) for row in matrix]
    traces = [{"type": "scatter", "mode": "lines+markers" if style == "line" else "markers", "name": headers[y],
               "x": [row[x] for row in matrix], "y": [row[y] for row in matrix]} for y in ys]
    facts = [_fact("inline.row_count", len(rows), "count"), _fact("inline.column_count", len(headers), "count")]
    for column, header in enumerate(headers):
        values = [row[column] for row in matrix]
        unit, subject = _header_unit(header), f"column:{column}"
        facts.append(_fact("inline.column", header, subject=subject))
        for key, value in {"minimum": min(values), "maximum": max(values), "mean": math.fsum(values) / len(values), "first": values[0], "last": values[-1]}.items():
            facts.append(_fact(f"inline.{key}", value, unit, subject))
    return ParameterResult("输入数据图", headers, rows, facts,
        "逐行解析用户提供的数值表；保留原始行序、列名与所有数值，用所选列绘图。",
        ["数据来源为本次输入，未验证其测量或计算方法；连线不表示插值精度、拟合或因果关系。"],
        {**params, "x_column": x, "y_columns": ys, "style": style},
        {"data": traces, "layout": {"title": "输入数据图", "xaxis": {"title": headers[x]}, "yaxis": {"title": headers[ys[0]] if len(ys) == 1 else "数值"}}},
        origin="USER_TEXT_DATA", details={"textHash": hashlib.sha256(params["data_text"].encode("utf-8")).hexdigest()})


def _crystal(params: dict[str, Any]) -> ParameterResult:
    from pymatgen.core import Lattice, Structure
    prototype, elements, a = params["prototype"], params["elements"], params["lattice_a_angstrom"]
    binary = prototype in {"rocksalt", "cscl"}
    if len(elements) != (2 if binary else 1):
        raise ValueError("岩盐与 CsCl 原型需要两个元素，其余已支持原型需要一个元素。")
    if "lattice_c_angstrom" in params and prototype != "hcp":
        raise ValueError("只有 HCP 原型使用独立的 c 参数；立方原型的三条边相等。")
    fcc = [[0, 0, 0], [0, .5, .5], [.5, 0, .5], [.5, .5, 0]]
    basis = {
        "sc": [[0, 0, 0]], "bcc": [[0, 0, 0], [.5, .5, .5]], "fcc": fcc,
        "diamond": fcc + [[(value + .25) % 1 for value in site] for site in fcc],
        "rocksalt": fcc + [[(site[0] + .5) % 1, site[1], site[2]] for site in fcc],
        "cscl": [[0, 0, 0], [.5, .5, .5]], "hcp": [[0, 0, 0], [2 / 3, 1 / 3, .5]],
    }[prototype]
    c = params.get("lattice_c_angstrom", a * math.sqrt(8 / 3)) if prototype == "hcp" else a
    nearest = {"sc": a, "bcc": a * math.sqrt(3) / 2, "fcc": a / math.sqrt(2), "diamond": a * math.sqrt(3) / 4,
               "rocksalt": a / 2, "cscl": a * math.sqrt(3) / 2, "hcp": min(a, c, math.sqrt(a * a / 3 + c * c / 4))}[prototype]
    species = [elements[0]] * len(basis) if not binary else [elements[0]] * (len(basis) // 2) + [elements[1]] * (len(basis) // 2)
    structure = Structure(Lattice.hexagonal(a, c) if prototype == "hcp" else Lattice.cubic(a), species, basis)
    repetitions = [int(value) for value in params.get("repetitions", [1, 1, 1])]
    structure.make_supercell(repetitions)
    if len(structure) > 256:
        raise ValueError("理想晶格超出 256 个位点的展示范围，请缩小重复数。")
    facts = [_fact("model.prototype", prototype), _fact("model.formula", structure.composition.reduced_formula),
        _fact("model.site_count", len(structure), "count"), _fact("model.lattice_a", a, "angstrom"),
        _fact("model.lattice_c", c, "angstrom"), _fact("model.cell_volume", float(structure.volume), "angstrom^3"),
        _fact("model.nearest_distance", nearest, "angstrom")]
    rows = [{"属性": label, "数值": value, "单位": unit} for label, value, unit in (
        ("原型", prototype.upper(), ""), ("化学式", structure.composition.reduced_formula, ""),
        ("位点数", len(structure), ""), ("单胞 a", a, "Å"), ("单胞 c", c, "Å"),
        ("展示晶胞体积", float(structure.volume), "Å³"), ("最短周期近邻距离", nearest, "Å"))]
    return ParameterResult(f"理想 {prototype.upper()} 晶格", ["属性", "数值", "单位"], rows, facts,
        "按指定原型的分数坐标和晶格参数生成理想晶胞及有界超晶胞；连接仅表示最短周期近邻。",
        ["这是理想模型，不代表用户样品、稳定相或结构弛豫结果；近邻连接不表示确定化学键或键级。"],
        {**params, "repetitions": repetitions, **({"lattice_c_angstrom": c} if prototype == "hcp" else {})},
        model=structure, origin="IDEAL_MODEL", details={"nearestDistance": nearest})


def compute_parameters(tool_id: str, params: dict[str, Any]) -> ParameterResult:
    validate_parameters(tool_id, params)
    try:
        return {"reference.convert_units": _convert, "generation.function_curve": _curves,
                "composition.from_formula": _composition, "viz.inline_xy": _inline,
                "generation.ideal_crystal": _crystal}[tool_id](params)
    except (OverflowError, ArithmeticError) as exc:
        raise ValueError("当前参数超出数值计算范围，请缩小输入范围。") from exc


def result_table(tool_id: str, params: dict[str, Any], result: ParameterResult) -> dict[str, Any]:
    return {"schemaVersion": "mdi.project.parameter-table/1.0", "artifactType": tool_id,
        "title": result.title, "columns": result.columns, "rows": result.rows, "facts": result.facts,
        "method": result.method, "limitations": result.limitations, "inputOrigin": result.origin,
        "sampleAnalysis": False, "inputHash": parameter_hash(params), "parameters": params,
        "resolvedParameters": result.resolved, **result.details}


def result_plot(tool_id: str, params: dict[str, Any], result: ParameterResult) -> dict[str, Any]:
    return {"schemaVersion": "mdi.project.parameter-figure/1.0", "artifactType": tool_id,
        "title": result.title, "plotlyFigure": result.figure, "inputOrigin": result.origin,
        "sampleAnalysis": False, "inputHash": parameter_hash(params)}


def result_scene(tool_id: str, params: dict[str, Any], result: ParameterResult, context: ToolExecutionContext) -> dict[str, Any]:
    from .structure import _viewer_scene_v1_payload
    # Reuse the established geometry and periodic-endpoint contract. A model
    # parameter identity is explicit; no sample or Dataset id is synthesized.
    scene, _ = _viewer_scene_v1_payload(result.title, result.model, params={
        "max_sites": 256, "max_bonds": 2048, "include_fractional_positions": True,
        "include_bonds": True, "bond_cutoff_angstrom": result.details["nearestDistance"] * (1 + 1e-6),
        "style_preset": "default", "camera_preset": "auto"}, tool_id=tool_id, context=context)
    scene["source"] = {"resource_type": "ideal_model", "resource_id": "parameters:" + parameter_hash(params),
                       "filename": "ideal_crystal.json", "tool_id": tool_id}
    scene["metadata"].update(title=result.title, model_kind="ideal_crystal", input_origin="IDEAL_MODEL",
        connectivity={"kind": "distance_neighbors", "method": "ideal_first_shell", "chemical_bond_claim": False})
    scene["provenance"].update(input_origin="IDEAL_MODEL", parameter_hash=parameter_hash(params), sample_analysis=False)
    if not validate_viewer_scene(scene).valid:
        raise ValueError("生成的理想晶格未通过几何校验，请调整晶格或重复参数。")
    return scene


class ProjectParameterAdapter(BaseToolAdapter):
    adapter_version = "1.0.0"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> Any:
        if input_refs or context.dataset_id is not None:
            raise ToolExecutionError("TOOL_INPUT_INVALID", "此工具使用显式参数或文本，不能隐式绑定样品。", self.tool_id)
        try:
            validate_parameters(self.tool_id, params)
        except ValueError as exc:
            raise ToolExecutionError("TOOL_PARAM_INVALID", str(exc), self.tool_id) from exc
        self._resolved_params = dict(params)
        self._input_hashes = [parameter_hash(params)]
        if self.tool_id == "reference.convert_units":
            self._input_hashes.append(SI_REFERENCE_SOURCE.contentHash)
        return params

    def run(self, prepared: Any, params: dict[str, Any]) -> ParameterResult:
        try:
            return compute_parameters(self.tool_id, params)
        except (ValueError, csv.Error) as exc:
            raise ToolExecutionError("TOOL_PARAM_INVALID", str(exc), self.tool_id) from exc

    def export(self, result: ParameterResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        params = self._resolved_params
        table = result_table(self.tool_id, params, result)
        references = [SI_REFERENCE_SOURCE.model_dump(mode="json")] if self.tool_id == "reference.convert_units" else []
        input_source = {"kind": result.origin, "contentHash": parameter_hash(params), "parameters": params}
        recipe = self.recipe_payload(name=result.title, params=params, artifact_types=artifact_types)
        recipe["inputRequirements"] = [input_source, *({"kind": "PLATFORM_REFERENCE", **source} for source in references)]
        definitions = {
            ArtifactType.table_json: ("calculation_values.json", table, "application/json"),
            ArtifactType.summary_md: ("summary.md", f"# {result.title}\n\n{result.method}\n\n" + "\n".join(result.limitations), "text/markdown"),
            ArtifactType.recipe_json: ("recipe.json", recipe, "application/json"),
        }
        if result.figure is not None:
            definitions[ArtifactType.plotly_json] = ("calculation_figure.json", result_plot(self.tool_id, params, result), "application/json")
        if result.model is not None:
            definitions[ArtifactType.structure_json] = ("ideal_crystal.json", result_scene(self.tool_id, params, result, self.context), "application/json")
        payloads = []
        for kind in artifact_types:
            if kind not in definitions:
                raise ToolExecutionError("TOOL_PARAM_INVALID", "此计算不支持请求的输出类型。", self.tool_id)
            name, content, media = definitions[kind]
            payloads.append(ArtifactPayload(file_name=name, artifact_type=kind,
                content=(content if isinstance(content, str) else stable_json_dumps(content)).encode("utf-8"), media_type=media))
        return self.export_payloads(payloads, {"inputOrigin": result.origin, "sampleAnalysis": False,
            "inputHash": parameter_hash(params), "referenceSources": references})

class UnitConversionAdapter(ProjectParameterAdapter):
    tool_id = "reference.convert_units"


class FunctionCurveAdapter(ProjectParameterAdapter):
    tool_id = "generation.function_curve"


class FormulaCompositionAdapter(ProjectParameterAdapter):
    tool_id = "composition.from_formula"


class InlineXYAdapter(ProjectParameterAdapter):
    tool_id = "viz.inline_xy"


class IdealCrystalAdapter(ProjectParameterAdapter):
    tool_id = "generation.ideal_crystal"
