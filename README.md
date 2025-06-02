<h1>Python newtonian telescope collimator application</h1>

<p>This application was created out of the need to use the OCAL 2 PRO telescope collimator on the Linux operating system.</p>


<h2>Linux installation</h2>


<p>Create a virtual environment</p>
<pre><code>python3 -m venv pycol</code></pre>
<p>Activate the virtual environment</p>
<pre><code>source pycol/bin/activate</code></pre>
<p>Install the required packages</p>
<pre><code>pip install -r requirements.txt</code></pre>
<p>Run the application</p>
<pre><code>python main.py</code></pre>
<p>At application startup on Linux machines, if the windows appear centered on the screen, it's a Wayland protocol 'feature' which, 
    currently does not allow window positioning via code. X11 does allow window start positioning. 
    If this is an issue for you, please start the session using X11.</p>


<h2>Windows installation</h2>
<p>Download the latest release from <a href="https://github.com/yourusername/pycol/releases/latest">GitHub Releases</a> and extract it.</p>
<p>Create a virtual environment</p>
<pre><code>python -m venv pycol</code></pre>
<p>Activate the virtual environment</p>
<pre><code>pycol\Scripts\activate</code></pre>
<p>Install the required packages</p>
<pre><code>pip install -r requirements.txt</code></pre>
<p>Run the application</p>
<pre><code>python main.py</code></pre>



<h3>Testing Video Capture Properties with opencv for OCAL 2 PRO camera:</h3>
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


















