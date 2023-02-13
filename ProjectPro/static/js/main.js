
function completed(payer_id) {
    $.post('/updatePay', {'payer_id' : payer_id}, function(data) {
        
        bill_status = $('#' + payer_id)
        if (bill_status.html()=="Completed") {
            bill_status.html("Not Completed")
            bill_status.addClass("Not Completed")
        }
        else if (bill_status.html()=="Not Completed") {
            bill_status.html("Completed")
            bill_status.addClass("Completed")
        }
    })
}

function deleted(payer_id) {
    $.post('/deletePay', {'payer_id' : payer_id}, function(data) {
        bill_status = $('.' + payer_id+"-info")
        bill_status.empty()
    })
}

function addHousemate() {
    userForm = $('#original')
    bill_name = $("#listItems").val()
    total = $("#billTotal").val()
    userForm.append(
    '<div id="new">\
        <label for="email"> EMAIL! </label>\
        <input type="email" name="email" placeholder="Enter Email...">\
        <label for="email"> BILL NAME! </label>\
        <select name="list_name">\
            <div id="billList">\
                <option>'+bill_name+'</option>\
            </div>\
        </select>\
        <label for="total"> TOTAL! </label>\
        <input type="number" name="total" placeholder="Bill Total..." id="billTotal" value='+total+' readonly>\
        <label for="share"> SHARE! </label>\
        <input type="number" name="share" placeholder="Enter Share...">\
        <br>\
    </div>');
}

function deleteHousemate() {
    $("div").remove("#new");
}