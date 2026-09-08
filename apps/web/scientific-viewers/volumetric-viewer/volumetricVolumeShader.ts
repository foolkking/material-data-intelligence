export const VOLUME_SHADER_VERSION = "phase10j6.volume_ray_march.v1" as const;

export const VOLUME_VERTEX_SHADER = /* glsl */ `
in vec3 position;
uniform mat4 modelViewMatrix;
uniform mat4 projectionMatrix;
out vec3 vUnit;
void main() {
  vUnit = position + vec3(0.5);
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

export const VOLUME_FRAGMENT_SHADER = /* glsl */ `
precision highp float;
precision highp sampler3D;
in vec3 vUnit;
uniform sampler3D uVolume;
uniform sampler2D uStructureDepth;
uniform vec3 uCameraUnit;
uniform mat4 uInverseProjectionView;
uniform mat4 uWorldToVolume;
uniform vec2 uDepthViewport;
uniform bool uHasStructureDepth;
uniform vec3 uGridShape;
uniform vec2 uWindow;
uniform float uOpacityScale;
uniform float uSamplesPerVoxel;
uniform int uMaximumSteps;
uniform int uPalette;
uniform bool uTransparentZero;
uniform bool uClipEnabled;
uniform int uClipAxis;
uniform float uClipOffset;
out vec4 outputColor;

vec2 intersectUnitBox(vec3 origin, vec3 direction) {
  vec3 inverseDirection = 1.0 / direction;
  vec3 first = (vec3(0.0) - origin) * inverseDirection;
  vec3 second = (vec3(1.0) - origin) * inverseDirection;
  vec3 minimums = min(first, second);
  vec3 maximums = max(first, second);
  return vec2(max(max(minimums.x, minimums.y), minimums.z), min(min(maximums.x, maximums.y), maximums.z));
}

vec3 palette(float value) {
  if (uPalette == 1) return vec3(value, 0.25 + 0.35 * (1.0 - abs(value * 2.0 - 1.0)), 1.0 - value);
  if (uPalette == 2) return vec3(min(1.0, value * 1.4), value * value * 0.75, 0.2 + value * 0.25);
  if (uPalette == 3) return vec3(0.08 + value * 0.92, 0.38 + value * 0.57, 0.42 - value * 0.3);
  return vec3(0.25 + value * 0.55, 0.08 + value * 0.82, 0.35 + (1.0 - value) * 0.35);
}

void main() {
  vec3 direction = normalize(vUnit - uCameraUnit);
  vec2 hit = intersectUnitBox(uCameraUnit, direction);
  float entry = max(hit.x, 0.0);
  float exitDistance = hit.y;
  if (uHasStructureDepth) {
    vec2 depthUv = gl_FragCoord.xy / uDepthViewport;
    float structureDepth = texture(uStructureDepth, depthUv).r;
    if (structureDepth < 1.0) {
      vec4 structureClip = vec4(depthUv * 2.0 - 1.0, structureDepth * 2.0 - 1.0, 1.0);
      vec4 structureWorld = uInverseProjectionView * structureClip;
      structureWorld /= structureWorld.w;
      vec3 structureUnit = (uWorldToVolume * structureWorld).xyz + vec3(0.5);
      float structureDistance = dot(structureUnit - uCameraUnit, direction);
      if (structureDistance > entry && structureDistance < exitDistance) exitDistance = structureDistance;
    }
  }
  if (exitDistance <= entry) discard;
  float voxelLength = length(direction * uGridShape) * (exitDistance - entry);
  int requestedSteps = int(ceil(voxelLength * uSamplesPerVoxel));
  int stepCount = clamp(requestedSteps, 1, uMaximumSteps);
  float stepDistance = (exitDistance - entry) / float(stepCount);
  float referenceStep = 1.0 / max(max(uGridShape.x, uGridShape.y), uGridShape.z);
  vec3 color = vec3(0.0);
  float alpha = 0.0;
  for (int index = 0; index < 768; index += 1) {
    if (index >= stepCount || alpha >= 0.985) break;
    float distanceValue = entry + (float(index) + 0.5) * stepDistance;
    vec3 point = uCameraUnit + direction * distanceValue;
    if (uClipEnabled) {
      float coordinate = uClipAxis == 0 ? point.x : (uClipAxis == 1 ? point.y : point.z);
      if (coordinate > uClipOffset) continue;
    }
    float sourceValue = texture(uVolume, vec3(point.z, point.y, point.x)).r;
    float normalized = clamp((sourceValue - uWindow.x) / (uWindow.y - uWindow.x), 0.0, 1.0);
    float alphaReference = normalized * uOpacityScale;
    if (uTransparentZero) alphaReference *= smoothstep(0.03, 0.12, abs(normalized - 0.5));
    float sampleAlpha = 1.0 - pow(max(0.0, 1.0 - alphaReference), stepDistance / referenceStep);
    vec3 sampleColor = palette(normalized);
    color += (1.0 - alpha) * sampleAlpha * sampleColor;
    alpha += (1.0 - alpha) * sampleAlpha;
  }
  if (alpha <= 0.001) discard;
  outputColor = vec4(color, alpha);
}
`;

export function validateVolumeShaderProgram(context: WebGL2RenderingContext): Readonly<{ linked: true }> {
  const compile = (type: number, source: string) => {
    const shader = context.createShader(type);
    if (!shader) throw new Error("shader_allocation_failed");
    context.shaderSource(shader, `#version 300 es\n${source}`);
    context.compileShader(shader);
    if (!context.getShaderParameter(shader, context.COMPILE_STATUS)) {
      context.deleteShader(shader);
      throw new Error("shader_compile_failed");
    }
    return shader;
  };
  const vertex = compile(context.VERTEX_SHADER, VOLUME_VERTEX_SHADER);
  const fragment = compile(context.FRAGMENT_SHADER, VOLUME_FRAGMENT_SHADER);
  const program = context.createProgram();
  if (!program) {
    context.deleteShader(vertex);
    context.deleteShader(fragment);
    throw new Error("program_allocation_failed");
  }
  try {
    context.attachShader(program, vertex);
    context.attachShader(program, fragment);
    context.linkProgram(program);
    if (!context.getProgramParameter(program, context.LINK_STATUS)) throw new Error("shader_link_failed");
    return Object.freeze({ linked: true });
  } finally {
    context.deleteProgram(program);
    context.deleteShader(vertex);
    context.deleteShader(fragment);
  }
}
