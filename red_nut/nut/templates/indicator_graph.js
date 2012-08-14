toto = new Highcharts.Chart(
        {chart: {renderTo: 'graph', defaultSeriesType: 'spline', backgroundColor: '#ebebeb', },
            legend: {}, title: {text: null},
            xAxis: {categories: [{% for p in graph_date %}"{{ p }}",{% endfor %}]},
            yAxis: {title: {text: null},},
            series: [{%for line in graph_data %}{name: "{{ line.name }}", data: {{ line.data }} },{% endfor %}],
            tooltip: {formatter: function() {return ''+ this.series.name +': '+this.y;} },
            plotOptions: {line: {animation: false, enableMouseTracking: false,
                                    dataLabels: {enabled: true, formatter: function()
                                                  {if (this.y == '-0') { return "0" } else
                                                    { return '' + this.y.toString().replace('.', ',');}
                                                  }
                                                }
                                  }
                         },
            exporting: {enabled: true}, credits: {enabled: true, text: "© CROIX ROUGE", href: null},
        });
