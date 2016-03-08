<h2>pyb</h2>
<p>a tool for web bench

</p>
<h2>usage:</h2>
<pre><code class="lang-javascript">python setup.py install
pyb -n 20 -c 2 -m POST -d 'name=lu&id=1' 'http://www.test.com/action'
pyb -n 200 -c 10  'http://www.test.com'</code></pre>
<h2>result:</h2>
<ul>
<li>rps : Requests per second</li>
<li>rate ：Transfer rate</li>
<li>avg_time ：Time per request</li>
</ul>
<pre><code class="lang-javascript">{
    'rps': '34.61',         # Requests per second
    'rate': '4.43',         # Transfer rate
    'avg_time': '0.03',     # Time per request
    'avg_length': '131.00',
    'total_req': 10,
    'succeed_req': 10,
    'failed_req': 0,
    'total_time': '0.29',
    'total_length': 1310.0
}</code></pre>
<h2>helper:</h2>
<pre><code class="lang-javascript">pyb -h
usage: pyb.py [-h] [-v] [-n REQUESTS] [-c CONCURRENCY]
              [-m {GET,POST,DELETE,PUT,HEAD,OPTIONS}] [-d DATA]
              [url]

positional arguments:
  url                   URL to hit

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         Displays version and exits.
  -n REQUESTS, --requests REQUESTS
                        Number of requests
  -c CONCURRENCY, --concurrency CONCURRENCY
                        Concurrency
  -m {GET,POST,DELETE,PUT,HEAD,OPTIONS}, --method {GET,POST,DELETE,PUT,HEAD,OPTIONS}
                        HTTP Method
  -d DATA, --data DATA  Request Data, for example: "id=1&amp;name=lu"</code></pre>
<p>