# Units and Properties

Time accepts femtosecond or picosecond; canonical parser output is expected to use femtosecond. Positions are fractional or angstrom according to trajectory mode. Velocities are Cartesian angstrom per femtosecond. Forces are Cartesian electronvolt per angstrom.

Energy is a total-system object with explicit potential, kinetic, total, and free slots in electronvolt; at least one value is present. Temperature is finite nonnegative kelvin and is never inferred by a viewer. Stress is `DEFERRED_BY_DESIGN` because tensor ordering, sign, and source conventions require a separate decision.

Property availability is strict: a top-level true flag requires the property in every frame, and false requires null in every frame. Arbitrary per-atom property maps are forbidden in v1.
