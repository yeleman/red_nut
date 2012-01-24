toto = new Highcharts.Chart(
        {chart: {renderTo: 'graph', defaultSeriesType: 'line', backgroundColor: '#ebebeb', },
            legend: {}, title: {text: null},
            xAxis: {categories: [{% for p in graph_date %}"{{ p }}",{% endfor %}]},
            yAxis: {title: {text: null},},
            series: [{%for line in graph_data %}{name: "{{ line.name }}", data: {{ line.data }} },{% endfor %}],
            tooltip: {formatter: function() {return ''+ this.series.name;} },
            plotOptions: {line: {animation: false, dataLabels: {enabled: true}, enableMouseTracking: false },
                          column: {animation: false, enableMouseTracking: false,
                          dataLabels: {enabled: true, formatter: function()
                          {if (this.y == '-0') { return "n/a" } else
                          { return '' + this.y.toString().replace('.', ',');} }} }},
            exporting: {enabled: true}, credits: {enabled: true, text: "© CROIX ROUGE", href: null},
        });
