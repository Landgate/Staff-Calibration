(function ($) {
	var ctx = document.getElementById('myChart').getContext('2d');
	Chart.defaults.global.defaultFontColor = 'black';
	Chart.defaults.global.defaultFontSize = '12';
	var myChart = new Chart(ctx, {
	type: 'bar',
	data: {
	        labels: {{ labels|safe }}, /*['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],*/
	        datasets: [{
	            label: 'Difference from mean',
	            data: {{ data|safe }},/*[12, 19, 3, 5, 2, 3],*/
	            backgroundColor: [
	                '#00876c',
	                '#39956a',
	                '#5ba268',
	                '#7caf67',
	                '#9dbb66',
	                '#bfc669',
	                '#e2cf6f',
	                '#e5b95d',
	                '#e6a250',
	                '#e68a49',
	                '#e37248',
	                '#dd584b',
	            ],
	            borderColor: [
	                '#00876c',
	                '#39956a',
	                '#5ba268',
	                '#7caf67',
	                '#9dbb66',
	                '#bfc669',
	                '#e2cf6f',
	                '#e5b95d',
	                '#e6a250',
	                '#e68a49',
	                '#e37248',
	                '#dd584b',
	            ],
	            pointRadius: 5,
	        }]
	    },
	    options: {
	        responsive: true,
	        legend: {
	          position: 'bottom',
	        },
	        hover: {
	          mode: 'index'
	        },
	        scales: {
	          xAxes: [{
	            display: true,
	            scaleLabel: {
	              display: true,
	              labelString: 'Month'
	            }
	          }],
	          yAxes: [{
	            display: true,
	            scaleLabel: {
	              display: true,
	              labelString: 'Difference in mm'
	            }
	          }]
	        },
	        title: {
	          display: true,
	          //text: 'Difference from mean height difference between Pin 1 & 21 '
	        },
	        tooltips: {
	            callbacks: {
	                label: function(tooltipItem, data) {
	                    var label = data.datasets[tooltipItem.datasetIndex].label || '';

	                    if (label) {
	                        label += ': ';
	                    }
	                    label += tooltipItem.yLabel.toFixed(2);
	                    return label;
	                }
	            }
	        }
	    }
	});

})();
