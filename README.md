<h1>Python OCAL 2 PRO collimator application</h1>

<p>This application was created out of the need to use the OCAL 2 PRO telescope collimator on the Linux operating system.</p>


<p>At application startup on Linux machines, if the windows appear centered on the screen, it is likely due to the Wayland protocol which, with the Qt libraries, currently does not allow window positioning via code. X11 does allow window movement. If this is an issue for you, please start the session using X11.</p>

<h3>Testing Video Capture Properties with opencv:</h3>
<ul>
    <li>CAP_PROP_POS_MSEC: TEST OK</li>
    <li>CAP_PROP_POS_FRAMES: Not supported by this device.</li>
    <li>CAP_PROP_POS_AVI_RATIO: Not supported by this device.</li>
    <li>CAP_PROP_FRAME_WIDTH: TEST OK</li>
    <li>CAP_PROP_FRAME_HEIGHT: TEST OK</li>
    <li>CAP_PROP_FPS: TEST OK</li>
    <li>CAP_PROP_FOURCC: TEST OK</li>
    <li>CAP_PROP_FRAME_COUNT: Not supported by this device.</li>
    <li>CAP_PROP_BRIGHTNESS: TEST OK</li>
    <li>CAP_PROP_CONTRAST: TEST OK</li>
    <li>CAP_PROP_SATURATION: TEST OK</li>
    <li>CAP_PROP_HUE: TEST OK</li>
    <li>CAP_PROP_GAIN: Not supported by this device.</li>
    <li>CAP_PROP_EXPOSURE: TEST OK</li>
    <li>CAP_PROP_CONVERT_RGB: TEST OK</li>
    <li>CAP_PROP_ZOOM: Not supported by this device.</li>
    <li>CAP_PROP_FOCUS: TEST OK</li>
</ul>
















