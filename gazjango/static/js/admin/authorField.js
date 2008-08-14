authors_display_id = 'id_authors_0';
author_add_id      = 'id_authors_1';
authors_hidden_id  = 'id_authors_2';

author_link_id_prefix = 'author-';

function addAuthor() {
    extra = $('#' + author_add_id);
    name = extra.val();
    if (name.length > 0) {
        $.ajax({
            type: "POST",
            url: "/data/usernames/",
            data: { name: name },
            success: function(username) {
                addAuthorToList(name, username);
                extra.val('');
            },
            error: function(request, status, errorThrown) {
                alert("Apparently you don't have permissions to create a new author. Talk to someone who does.");
            }
        });
    }
    return false;
}

function authorLinkFor(name, username) {
    return '<a href="#" id="' + author_link_id_prefix + username + '" onclick="return removeAuthor(\'' + username + '\');">' + name + '</a>';
}

if (!Array.indexOf) {
    Array.prototype.indexOf = function(el) {
        for (var i = 0; i < this.length; i++) {
            if (this[i] == el) {
                return i;
            }
        }
        return -1;
    }
}

function addAuthorToList(name, username) {
    var authors = $('#' + authors_hidden_id);
    split = jQuery.trim(authors.val()).split(/\s+/);
    if (split.indexOf(username) == -1) {
        $('#' + authors_display_id).append(' ' + authorLinkFor(name, username));
        authors.val(authors.val() + ' ' + username);
    }
}

function removeAuthor(username) {
    $('#' + author_link_id_prefix + username).remove();

    authors = $('#' + authors_hidden_id);
    split = jQuery.trim(authors.val()).split(/\s+/);
    new_authors = [];
    for (i = 0; i < split.length; i++) {
        if (split[i] != username) {
            new_authors.push(split[i]);
        }
    }
    authors.val(new_authors.join(' '));
}

function setAutocomplete() {
    $('#' + author_add_id).autocomplete(
        '/data/authors/',
        {
            formatItem: function(row) { return row[0] + " (" + row[1] + ")"; },
            onItemSelect: addAuthor
        }
    );
}

$(document).ready(setAutocomplete);
