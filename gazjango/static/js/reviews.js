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
var estabsByType = {}; // type => [estab_id, ...]
var estabsByLoc = {};  // num => [estab_id, ...]
var establishment_nums = []; // list of all estab_ids

var typeShown = {};  // type => bool
var locShown = {};   // loc => bool
var tagChecked = {}; // tag_id => bool
var showAllTags = true;

function initializeMap(element) {
    map = new GMap2(element);
    map.setCenter(new GLatLng(39.9034, -75.3529), 15);
    map.addControl(new GMapTypeControl());
    map.addControl(new GLargeMapControl());
}

function addMarker(num, point, info_box, type, loc, tags) {
    var marker = new GMarker(point, icons[type]);
    GEvent.addListener(marker, 'click', function() {
        map.openInfoWindowHtml(point, info_box);
    });
    map.addOverlay(marker);
    
    establishments[num] = { 'num': num, 'marker': marker, 'info': info_box, 
                    'type': type, 'loc': loc, 'tags': tags, 'tagHiders': [] };
    estabsByType[type].push(num);
    estabsByLoc[loc].push(num);
    establishment_nums.push(num);
}

function synchronizeCheckboxes() {
    type_prefix_length = 'type-checkbox-'.length
    $('.type-checkbox').each(function() {
        type = this.id.substring(type_prefix_length);
        typeShown[type] = this.checked;
    });
    
    loc_prefix_length = 'loc-checkbox-'.length
    $('.loc-checkbox').each(function() {
        loc = this.id.substring(loc_prefix_length);
        locShown[loc] = this.checked;
    });
    
    tag_prefix_length = 'tag-checkbox-'.length
    $('.tag-checkbox').each(function() { 
        tag = parseInt(this.id.substring(tag_prefix_length));
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
function setLoc(type, value) {
    locShown[type] = value;
    updateEstablishments(estabsByLoc[type]);
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
        if (typeShown[est.type] && locShown[est.loc]
               && (showAllTags || shouldShowWithTags(est.tags))) {
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
