toto = new Highcharts.Chart(
        {chart: {renderTo: 'graph', defaultSeriesType: 'line', backgroundColor: '#ebebeb', },
            legend: {}, title: {text: null},
            xAxis: {categories: ["un", "deux", "trois"]},
            yAxis: {title: {text: null},},
            series: [{name: 'premier', data: [12, 73, 89]}],
            tooltip: {formatter: function() { return ''+ this.series.name;} },
            plotOptions: {line: {animation: false, dataLabels: {enabled: true}, enableMouseTracking: false },
                          column: {animation: false, enableMouseTracking: false,
                          dataLabels: {enabled: true, formatter: function()
                          {if (this.y == '-0') { return "n/a" } else
                          { return '' + this.y.toString().replace('.', ',');} }} }},
            exporting: {enabled: true}, credits: {enabled: true, text: "RIEN", href: null},
        });
