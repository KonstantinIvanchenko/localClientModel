$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    var numbers_received = [];

    //receive details from server
    socket.on('new_data', function(msg) {
        console.log("Received indices " + msg[0]);
        console.log("Received load " + msg[1]);
        console.log("Received temp " + msg[2]);
        console.log("Received memused " + msg[3]);
        console.log("Received memavai " + msg[4]);
        //maintain a list of ten numbers

        var ctx_load = document.getElementById("myChart_load");
        var ctx_memused = document.getElementById("myChart_virtMemUsed");

        var chart_Data = new Chart(ctx_load, {
          type: 'line',
          data: {
              labels: msg[0],
              datasets: [{
                  label: 'Cpu Load, %',
                  data: msg[1],
                  backgroundColor: [
                      'rgba(255, 99, 132, 0.2)',
                      'rgba(54, 162, 235, 0.2)',
                      'rgba(255, 206, 86, 0.2)',
                      'rgba(75, 192, 192, 0.2)',
                      'rgba(153, 102, 255, 0.2)',
                      'rgba(255, 159, 64, 0.2)'
                  ],
                  borderColor: [
                      'rgba(255,99,132,1)',
                      'rgba(54, 162, 235, 1)',
                      'rgba(255, 206, 86, 1)',
                      'rgba(75, 192, 192, 1)',
                      'rgba(153, 102, 255, 1)',
                      'rgba(255, 159, 64, 1)'
                  ],
                  borderWidth: 1
              }]
          },
          options: {
              scales: {
                  yAxes: [{
                      ticks: {
                          beginAtZero:true
                      }
                  }]
              },
              animation: false,
              responsive: true, 
              maintainAspectRatio: true
          }
      });

        var chart_Data = new Chart(ctx_memused, {
          type: 'line',
          data: {
              labels: msg[0],
              datasets: [{
                  label: 'Virtual Memory Used, Mb',
                  data: msg[3],
                  backgroundColor: [
                      'rgba(54, 162, 235, 0.2)',
                      'rgba(255, 99, 132, 0.2)',
                      'rgba(255, 206, 86, 0.2)',
                      'rgba(75, 192, 192, 0.2)',
                      'rgba(153, 102, 255, 0.2)',
                      'rgba(255, 159, 64, 0.2)'
                  ],
                  borderColor: [
                      'rgba(255,99,132,1)',
                      'rgba(54, 162, 235, 1)',
                      'rgba(255, 206, 86, 1)',
                      'rgba(75, 192, 192, 1)',
                      'rgba(153, 102, 255, 1)',
                      'rgba(255, 159, 64, 1)'
                  ],
                  borderWidth: 1
              }]
          },
          options: {
              scales: {
                  yAxes: [{
                      ticks: {
                          beginAtZero:false
                      }
                  }]
              },
              animation: false,
              responsive: true, 
              maintainAspectRatio: true
          }
      });     
  
    })
});
