x = 5;
$(document).ready(function(){
  var diameter = 800;

  // Color gradient from red to green.
  var color = d3.scale.linear()
      .domain([0,.5,1])
      .range(['red','yellow','green']);

  // Pack layout
  var pack = d3.layout.pack()
      .size([diameter - 4, diameter - 4])
      .value(function(d) { return d.size; });

  // SVG Element
  var svg = d3.select("#chart-container").append("svg")
      .attr("width", diameter)
      .attr("height", diameter)
      .append("g")
      .attr("transform", "translate(2,2)");

  // Div tag for tooltip.
  var tooltip = d3.select("body").append("div")
      .attr("class", "tooltip")
      .style("opacity", 1e-6);

  // Recureses into a node, computing the node feature support (between 0 and 1),
  // weighted by the value (size) of the node.
  function compute_support(d){
    if(d.support != undefined)
      return d.support;

    return d.support = d.children.reduce(
      function(cum,child){
        return cum + (child.value * compute_support(child)/d.value)
      },0);
  }

  // Compute text for mouseover.
  function compute_message(d){
    output = ""

    // Outer Bubble
    if(d.feature_name){
      output += "<h2>"+d.feature_name+"</h2>";
      output += "<p><b>" + (compute_support(d) * 100).toPrecision(2) + "%</b> global browser support</p>";
    }

    // Browser Family.
    if(d.family_name){
      output += "<h2>"+d.family_name+"</h2>";
      output += "<p><b>" + (compute_support(d) * 100).toPrecision(2) + "%</b> of users can use " + d.parent.feature_name + "</p>";
      output += "<p>Used by <b>" + d.value.toPrecision(2) + "%</b> of global users.</p>";
    }

    // Browser Version.
    if(d.version_name){
      output += "<h2>"+ d.parent.family_name + " v" + d.version_name + "</h2>";
      output += "<p><b>" + (d.support ? "Supports</b> " : "Doesn't support</b> ") + d.parent.parent.feature_name + "</p>";
      output += "<p>Used by <b>" + d.value.toPrecision(2) + "%</b> of global users.</p>";
    }

    return output
  }

  // Determines the color for a node
  function compute_color(d){
    return color(compute_support(d));
  }

  // Grabs the relevant portion of a name depending on space
  // Its better to just have "18" than "fox 18" for "firefox 18"
  // if you only have room for six characters.
  function limit_name(name,size){
    if(name.length < size)
      return name;

    name = name.split(' ').pop();
    return name.substring(0,size);
  }

  function mouseover(d,i){
    // Darken the color of the circle.
    d3.select(this)
      .transition()
      .duration(100)
      .style("fill",d3.rgb(this.style.fill).darker(.25));

    // Fade in the tooltip.
    tooltip
      .html(compute_message(d))
      .transition()
      .duration(500)
      .style("opacity", 1);
  }

  function mousemove(d,i){
    // The API returns the string "12px" instead of a number
    tt_height = tooltip[0][0].getBoundingClientRect().height
    tt_width = tooltip[0][0].getBoundingClientRect().width

    tooltip
      .style("left", (d3.event.pageX - 10 - tt_width) + "px")
      .style("top", (d3.event.pageY - 10 - tt_height) + "px");
  }

  function mouseout(d,i){
    // Return the color to normal.
    d3.select(this)
      .transition()
      .duration(200)
      .style("fill",compute_color);

    // Fade out the tooltip.
    tooltip
      .transition()
      .duration(500)
      .style("opacity", 0)
  }

  function update_chart(src){
    d3.json(src, function(error, root) {

      $('.content #feature-name').text(root.feature_name)
      $('.content #feature-description').text(root.feature_description)

      var node = svg.data([root])
                    .selectAll(".node")
                    .data(pack.nodes)

      node.enter()
          .append("g")
          .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; })
          .append("circle")
          .attr("r", function(d) { return d.r})
          .style("fill",compute_color)
          .on("mouseover",mouseover)
          .on("mousemove",mousemove)
          .on("mouseout",mouseout);

       node.exit().remove();

      node.filter(function(d) { return d.version_name; }).append("text")
          .attr("dy", ".3em")
          .style("text-anchor", "middle")
          .text(function(d) { return limit_name(d.parent.family_name + " " + d.version_name, d.r / 3); });

    });
  }

  function load_data(src){
    file = $("#data-chooser").val();
    location.hash = file;
    update_chart(file);
  }

  function update_feature_selector(data){
    // Load stats/index.json to fill out the selector
    choices = d3.select("select#data-chooser")
                .selectAll("option")
                .data(data);

    choices.enter()
           .append("option")
           .text(function(d){return d.title})
           .attr("value",function(d){return d.file});

    choices.exit().remove();
  }

  d3.json("stats/index.json",function(error, root){
    update_feature_selector(root.features);

    // Set the <select> value based on the location.hash
    file = location.hash.slice(1);
    if(root.features.filter(function(o){return o.file == file;}).length){
      $("#data-chooser").val(file);
    }

    // Load something interesting
    update_chart("stats/css-canvas.json");

    // Update the data on change
    $("#data-chooser").change(load_data);

    categories = d3.select("select#category-chooser");
    categories.selectAll("option")
              .data(["All"].concat(root.categories))
              .enter()
              .append("option")
              .text(String)
              .attr("value",String)

    $("#category-chooser").change(function(){
      category = this.value;

      // If they select "All", we return them all
      if(category == "All")
        update_feature_selector(root.features);

      // Otherwise we filter the data
      else {
        features = root.features.filter(function(feature){
          return feature['categories'].indexOf(category) >= 0;
        });
        update_feature_selector(features);
      }
    })
  });
})
