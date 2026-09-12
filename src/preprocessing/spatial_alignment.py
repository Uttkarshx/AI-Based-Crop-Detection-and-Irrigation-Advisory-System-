import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject


def align_array(
	values: np.ndarray,
	source_transform: rasterio.Affine,
	source_crs: rasterio.crs.CRS,
	target_shape: tuple[int, int],
	target_transform: rasterio.Affine,
	target_crs: rasterio.crs.CRS,
	categorical: bool = False,
) -> np.ndarray:
	destination = np.full(target_shape, np.nan, dtype=np.float32)
	reproject(
		source=values.astype(np.float32),
		destination=destination,
		src_transform=source_transform,
		src_crs=source_crs,
		dst_transform=target_transform,
		dst_crs=target_crs,
		resampling=Resampling.nearest if categorical else Resampling.bilinear,
		src_nodata=np.nan,
		dst_nodata=np.nan,
	)
	return destination
