// =========
// = Setup =
// =========

var map;
var icons = {}; // short_type => GIcon

var establishments = {}; // estab_id => { 'num': estab_id,
                         //               'marker': GMarker,
                         //               'info': "html str",
                         //               'type': "r",
                         //               'tags': [1, 5, 9],
                         //               'tagHiders': [1, 9] }
var estabsByType = {}; // type => [estab_id, estab_id, ...]
var estabsByTag  = {}; // tag_id => [estab_id, estab_id]

var typeHidden = {}; // type => true or false/undefined

function initializeMap(element) {
    map = new GMap2(element);
    map.setCenter(new GLatLng(39.9034, -75.3529), 15);
    map.addControl(new GMapTypeControl());
    map.addControl(new GLargeMapControl());
}

function addMarker(num, point, info_box, type, tags) {
    var marker = new GMarker(point, icons[type]);
    GEvent.addListener(marker, 'click', function() {
        map.openInfoWindowHtml(point, info_box);
    });
    map.addOverlay(marker);
    
    establishments[num] = { 'num': num, 'marker': marker, 'info': info_box, 
                            'type': type, 'tags': tags, 'tagHiders': [] };
    (estabsByType[type] || (estabsByType[type] = [])).push(num);
    jQuery.each(tags, function() {
        (estabsByTag[this] || (estabsByTag[this] = [])).push(num);
    });
}

function synchronizeCheckboxes() {
    $('.type-checkbox').each(function() { doTypeCheckbox(this); });
    $('.tag-checkbox').each(function(){ doTagCheckbox(this); });
}

// ====================
// = Hiding / Showing =
// ====================

// TODO: the table isn't properly highlighted when things are hidden

Array.prototype.deleteAll = function(el) {
    for (i = 0; i < this.length; i++) {
        if (this[i] == el) {
            this.splice(i, 1);
        }
    }
}

function hideType(type) {
    typeHidden[type] = true;
    jQuery.each(estabsByType[type], function() {
        var establishment = establishments[this];
        hideEstablishment(establishment);
    });
}
function showType(type) {
    typeHidden[type] = false;
    jQuery.each(estabsByType[type], function() {
        var establishment = establishments[this];
        if (establishment.tagHiders.length == 0) {
            showEstablishment(establishment);
        }
    });
}

function hideTag(tag) {
    jQuery.each(estabsByTag[tag], function() {
       var establishment = establishments[this];
       establishment.tagHiders.push(tag);
       hideEstablishment(establishment);
    });
}
function showTag(tag) {
    jQuery.each(estabsByTag[tag], function() {
        var establishment = establishments[this];
        establishment.tagHiders.deleteAll(tag);
        if (establishment.tagHiders.length == 0) {
            showEstablishment(establishment);
        }
    });
}

function showEstablishment(establishment) {
    establishment.marker.show();
    $('#establishment-' + establishment.num).show();
}
function hideEstablishment(establishment) {
    establishment.marker.hide();
    $('#establishment-' + establishment.num).hide();
}

function doTypeCheckbox(checkbox) {
    type = checkbox.id.substring('type-checkbox-'.length);
    doType(type, checkbox.checked);
}
function doTagCheckbox(checkbox) {
    tag = parseInt(checkbox.id.substring('tag-checkbox-'.length));
    doTag(tag, checkbox.checked);
}

function doType(type, checked) { checked ? showType(type) : hideType(type)}
function doTag(tag, checked) { checked ? showTag(tag) : hideTag(tag); }

// ===============
// = Other Stuff =
// ===============

function openInfo(num) {
    var est = establishments[num];
    est.marker.openInfoWindowHtml(est.info);
}
