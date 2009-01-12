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
var establishment_nums = []; // list of all estab_ids

var typeShown = {}; // type => true|false
var tagChecked = {}; // tag_id => true|false
var showAllTags = true;

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
    establishment_nums.push(num);
}

function synchronizeCheckboxes() {
    $('.type-checkbox').each(function() {
        type = this.id.substring('type-checkbox-'.length);
        typeShown[type] = this.checked;
    });
    $('.tag-checkbox').each(function() { 
        tag = parseInt(this.id.substring('tag-checkbox-'.length));
        tagChecked[tag] = this.checked;
    });
    updateShowAllTags();
    updateEstablishments(establishment_nums);
}

// ====================
// = Hiding / Showing =
// ====================

// TODO: the table isn't properly highlighted when things are hidden

function setType(type, value) {
    typeShown[type] = value;
    updateEstablishments(estabsByType[type]);
}
function setTag(tag, value) {
    tagChecked[tag] = value;
    updateShowAllTags();
    updateEstablishments(establishment_nums);
}

function updateShowAllTags() {
    showAllTags = true;
    jQuery.each(tagChecked, function(tag, checked) {
        if (checked) {
            showAllTags = false;
            return false; // break from each()
        }
    });
}
// doesn't account for showAllTags
function shouldShowWithTags(tags) {
    for (i = 0; i < tags.length; i++)
        if (tagChecked[tags[i]])
            return true;
    return false;
}
function updateEstablishments(list) {
    jQuery.each(list, function() {
        var est = establishments[this];
        if (typeShown[est.type] && (showAllTags || shouldShowWithTags(est.tags))) {
            showEstablishment(est);
        } else {
            hideEstablishment(est);
        }
    })
}

function showEstablishment(establishment) {
    establishment.marker.show();
    $('#establishment-' + establishment.num).show();
}
function hideEstablishment(establishment) {
    establishment.marker.hide();
    $('#establishment-' + establishment.num).hide();
}

// ===============
// = Other Stuff =
// ===============

function openInfo(num) {
    var est = establishments[num];
    est.marker.openInfoWindowHtml(est.info);
}

function setAll(kind, val) {
    $('.' + kind + '-checkbox').attr('checked', val);
    synchronizeCheckboxes();
}