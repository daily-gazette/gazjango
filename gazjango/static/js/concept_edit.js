function concept_edit() {
    var item = $(this).parent();
    var url = item.find(".title").attr("href");
    item.load("/staff/new/?ajax&name=" + escape(name),null, function () {
        $("#save-form").submit(concept_save);
    });
    return false;
}

$(document).ready(function () {
    $("ul.concept .edit").click(concept_edit);
})

function concept_save() {
    var item = $(this).parent();
    var data = {
        name: item.find("#id_name").val(),
        notes: item.find("#id_notes").val(),
        due: item.find("#id_due").val(),
        users: item.find("#id_users").val()        
    };
    $.post("/staff/new/?ajax",data,function(result) {
        if (result != "failure") {
            item.before($("li",result).get(0));
            item.remove();
            $("ul.concept .edit").click(concept_edit);
        }
        else {
            alert("Failed to validate the concept before saving.");
        }
    });
    return false;
}