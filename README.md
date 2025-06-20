<h1>Python newtonian telescope collimator application</h1>

This software is licensed under the GNU General Public License v3.  
See the [LICENSE](./Licence.txt) file for full details.

<p>This application was created out of the need to use the OCAL 2 PRO telescope collimator on Linux operating system.</p>

<h2>Requirements</h2>

<ul>
<li>Python version => Python 3.12.7 installed on your OS</li>
</ul>

<h2>Linux installation</h2>

<p>copy source code </p>

<p>Create a virtual environment</p>
<pre><code>python3 -m venv pycol</code></pre>
<p>Activate the virtual environment</p>
<pre><code>source pycol/bin/activate</code></pre>
<p>Install the required packages</p>
<pre><code>pip install -r requirements.txt</code></pre>
<p> <strong>Before starting the application change your focus.txt parameters provided by the manufacturer.</strong></p>
<p>Run the application</p>
<pre><code>python main.py</code></pre>


<h2>Windows installation (tested only on Windows 10)</h2>

<p>Create a virtual environment</p>
<pre><code>python -m venv pycol</code></pre>
<p>Activate the virtual environment</p>
<pre><code>pycol\Scripts\activate</code></pre>
<p>Install the required packages</p>
<pre><code>pip install -r requirements.txt</code></pre>
<p>Run the application</p>
<pre><code>python main.py</code></pre>



## Author

Created by Carlo Moisè (<carlo.moise@libero.it>) 



















