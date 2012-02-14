toto = new Highcharts.Chart(
        {chart: {renderTo: 'zscore', defaultSeriesType: 'column', backgroundColor: '#ebebeb', },
            legend: {}, title: {text: null},
            xAxis: {categories: [{% for p in graph_date %}"{{ p }}",{% endfor %}]},
            yAxis: {title: {text: null},},
            series: [{%for line in zscore_data %}{name: "{{ line.name }}", data: {{ line.data }} },{% endfor %}],
            tooltip: {formatter: function() {return ''+ this.series.name;} },
            plotOptions: {column: {animation: false, enableMouseTracking: false,
                                    dataLabels: {enabled: true, color: "ffeeee", formatter: function(){return '' + this.y.toString().replace('.', ','); }} 
                                  }
                        },
            exporting: {enabled: true}, credits: {enabled: true, text: "© CROIX ROUGE", href: null},
        });
