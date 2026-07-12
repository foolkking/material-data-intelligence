# Supercell Policy

Supercells are renderer-local view state and never alter canonical artifacts, resources, recipes, or backend job status. Offsets are positive and deterministic: `0..nx-1`, `0..ny-1`, `0..nz-1`.

Each axis is limited to 1 through 3. Applying a valid view refits the deterministic camera and clears active selection and unfinished measurement state. Reset returns to `1x1x1`.
