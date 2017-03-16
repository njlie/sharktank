/**
 * Created by seth on 2/25/17.
 */
google.charts.load('current', {'packages': ['corechart']});
google.charts.setOnLoadCallback(drawChart);

var categoryArray = google.visualization.DataTable(ideas);

function drawChart() {

    var data = google.visualization.arrayToDataTable([
        ['Category', 'Number of Pitches'],
        ['Software', 160],
        ['Engineering', 99],
        ['Social', 25],
        ['Political', 2],
        ['Metaphysical', 200],
        ['Misc', 35],
        ['Environmental', 77]
    ]);

    var options = {
        'title': 'Spread of ideas',
        'backgroundColor': 'transparent',
        'is3D': true
    };

    var chart = new google.visualization.PieChart(document.getElementById('piechart'));

    chart.draw(data, options);
}