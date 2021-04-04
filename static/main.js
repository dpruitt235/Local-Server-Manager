var serverInfoDefaultHolder;

$(document).ready(function(){
    serverInfoDefaultHolder = $('#serverClass').clone();
    serverInfoDefaultHolder.removeAttr('hidden');
    console.log(serverInfoDefaultHolder);
    var w = new Worker(updateLoop()); 
});

function updateLoop(){
    updateInfo();
    setTimeout("updateLoop()", 3000);
}

function sendStart(num){
    var info = {msg: 'start', srv: num};
    var test = JSON.stringify(info);
    sendPost(test);
    $('#vMC').html('&#128993'); // Yellow
}

function sendStop(num){
    var info = {msg: 'stop', srv: num};
    var test = JSON.stringify(info);
    sendPost(test);
    $('#vMC').html('&#128308');
}

function sendPost(str){
    $.ajax({
        method: "POST",
        url: "/",
        data: str,
        contentType: 'application/json',
        dataType: 'json'
    });
}

function updateInfo(){
    $.get("/update", function(data, status){
        try{
            $('#ramFree').html(data.ramFree);
            $('#ramPercent').html(data.ramPercent);
            $('#ramUsed').html(data.ramUsed);
            $('#ramTotal').html(data.ramTotal);
            $('#updateTime').html(data.time);

            var serverData = data.servers
            for(var i = 0; i < Object.keys(serverData).length; i++){
                // todo for each element, create a Server tag instance. Add it after the hidden element.
            }

            if (data.vanillia){
                $('#vMC').html('&#128994'); // Green
            }else{
                $('#vMC').html('&#128308'); // Red
            }
            if (data.forge){
                //$('').html('&#128994'); // Green
            }else{
                //$('').html('&#128308'); // Red
            }
        } catch (error){
            console.error(error);
        }
    })
}