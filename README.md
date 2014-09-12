# D3 Browser Feature Stats Visualization  

This app is hosted [here](http://mastahyeti.github.io/browserstats).

This application takes data from [caniuse](http://caniuse.com) and presents it in a pack chart powered by [D3](http://d3js.org). The innermost circles represent specific versions of web browsers. The next level of circles represent families of web browsers (Eg. Chrome, FireFox, IE). The color of the circles represents how well that browser supports the feature selected using the dropdown menu. Red means that the feature isn't supported. Green means that it is. These statistics bubble up from the specific browser version, to the browser-family, to the outermost circle -- the universe of web browsers. As this value bubbles up, it is weighted by the percentage of people using that given browser version.
