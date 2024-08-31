## Realtime RIFE interpolation script for MPV based on rife-ncnn-vulkan ##

interpMulti             = 2          # Framerate multiplier
interpModel             = 9         # Recommended 9 = rife-v4(supports over 2x multi) 5 = rife-2.3(higher quality only supports 2x)
gpuThread               = 2          # GPU Thread count for interpolation
gpuId                   = None       # GPU device to use
TTA                     = False      # Enable TTA(Test-Time Augmentation) mode
UHD                     = False      # Changes opticalflow resolution scale to 0.5 can have a positive or negative effect on interpolation quality
sceneDetection          = True       # Turn off interpolation for scenechanges to avoid warping
sceneDetectionThreshold = 0.15       # lower is more sensitive
SKIP                    = True      # don't interpolate duplicate frames to save performance
skipThreshold           = 52         # frame simularity threshold
osdInfo                 = False      # Display OSD info

cMatrix = '709'
cRange = 'limited'

import vapoursynth as vs
import fractions
core = vs.core

clip = video_in
colorlv = clip.get_frame(0).props._ColorRange
fmt_fin = clip.format.id

  
if container_fps > 0.1:
  clipFps = container_fps
else:
  clipFps = 23.97602

if clipFps >= 22 and clipFps <= 24.5:
  interpMulti = 2.5

if clipFps >= 24.9 and clipFps <= 26:
  interpMulti = 2.4

if clipFps >= 29 and clipFps <= 31:
  interpMulti = 2
  interpModel = 5

if clipFps > 31:
 sys.exit()  

core.log_message(1, str(clipFps))


def float_to_ratio(flt):
    if int(flt) == flt:
        return int(flt), 1
    flt_str = str(flt)
    flt_split = flt_str.split('.')
    numerator = int(''.join(flt_split))
    denominator = 10 ** len(flt_split[1])
    return numerator, denominator

ffps = (interpMulti, 1)
if isinstance(interpMulti, float):
  ffps = float_to_ratio(interpMulti)

# Make sure the input is not a duplicated frame
clip = core.misc.SCDetect(clip=clip,threshold=sceneDetectionThreshold)


aspect_radio = clip.width / clip.height
if aspect_radio > 2:
#                                 1747x760
	if (clip.width * clip.height) > 1271961:
		clip = clip.resize.Bicubic(width=int(728 * aspect_radio), height=728, format=vs.RGBS, matrix_in_s="709")
	else:
		clip = clip.resize.Bilinear(format=vs.RGBS, matrix_in_s="709")
else:
	if interpMulti > 2:
		#                                 1472x828
		if (clip.width * clip.height) > 1218816:
			clip = clip.resize.Bicubic(width=int(828 * aspect_radio) if aspect_radio != (16/9) else 1472, height=828, format=vs.RGBS, matrix_in_s="709")
		else:
			clip = clip.resize.Bilinear(format=vs.RGBS, matrix_in_s="709")
	else:
		#                                 1536x864
		if (clip.width * clip.height) > 1327104:
			clip = clip.resize.Bicubic(width=int(864 * aspect_radio) if aspect_radio != (16/9) else 1536, height=864, format=vs.RGBS, matrix_in_s="709")
		else:
			clip = clip.resize.Bilinear(format=vs.RGBS, matrix_in_s="709")

# interpolate with rife-ncnn

clip = core.rife.RIFE(clip,model=interpModel,factor_num=ffps[0],factor_den=ffps[1], gpu_id=gpuId,gpu_thread=gpuThread,tta=TTA,uhd=UHD,sc=sceneDetection,skip=SKIP,skip_threshold=skipThreshold)

clip = clip.resize.Bilinear(format=fmt_fin, matrix_s="709", range=1 if colorlv == 0 else None)

if osdInfo == True:
  if   interpModel == 0:  iModel = "RIFE "
  elif interpModel == 1:  iModel = "rife-HD "
  elif interpModel == 2:  iModel = "rife-UHD "
  elif interpModel == 3:  iModel = "rife-anime "
  elif interpModel == 4:  iModel = "rife-v2 "
  elif interpModel == 5:  iModel = "rife-v2.3 "
  elif interpModel == 6:  iModel = "rife-v2.4 "
  elif interpModel == 7:  iModel = "rife-v3.0 "
  elif interpModel == 8:  iModel = "rife-v3.1 "
  elif interpModel == 9:  iModel = "rife-v4 "
  elif interpModel == 10: iModel = "rife-v4-ES-SLOW "
  elif interpModel == 11: iModel = "rife-v4.1 "
  elif interpModel == 12: iModel = "rife-v4.1-ES-SLOW "
  elif interpModel == 13: iModel = "rife-v4.2 "
  elif interpModel == 14: iModel = "rife-v4.2-ES-SLOW "
  elif interpModel == 15: iModel = "rife-v4.3 "
  elif interpModel == 16: iModel = "rife-v4.3-ES-SLOW "
  elif interpModel == 17: iModel = "rife-v4.4 "
  elif interpModel == 18: iModel = "rife-v4.4-ES-SLOW "
  elif interpModel == 19: iModel = "rife-v4.5 "
  elif interpModel == 20: iModel = "rife-v4.5-ES "
  elif interpModel == 21: iModel = "rife-v4.6 "
  elif interpModel == 22: iModel = "rife-v4.6-ES "
  elif interpModel == 23: iModel = "sudo_rife4 "
  elif interpModel == 24: iModel = "sudo_rife4-ES-SLOW "
  elif interpModel == 25: iModel = "sudo_rife4-ES "
  clip = core.text.Text(clip, text=(iModel + str(interpMulti) + "x " + str(clip.width) + "x" + str(clip.height) + " @" + f"{(clipFps*interpMulti):.3f}" + "Hz") ,alignment=7, scale=1) 
  
  
fps_fraction = fractions.Fraction(container_fps * interpMulti).limit_denominator()
output_num, output_den = fps_fraction.numerator, fps_fraction.denominator
clip = core.std.AssumeFPS(clip, fpsnum=output_num, fpsden=output_den)

# output to mpv
clip.set_output()

