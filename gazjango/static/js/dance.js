// requires jQuery

var cornFreq = $.cookie("corns");
if (cornFreq == null || cornFreq < 4000) {
    cornFreq = 6000;
    $.cookie("corns", cornFreq);
}

var cornID;
function stopCorns() {
    cornFreq = -1;
    nameCornFreq();
    clearTimeout(cornID);
    cornID = undefined;
}
function startCorns() {
    if (cornFreq == -1) {
        return;
    }
    nameCornFreq();
    clearTimeout(cornID);
    cornID = setInterval(makeCornDancer, cornFreq);
}

function incCornFreq() {
    if (cornFreq == -1) {
        cornFreq = 4000;
    } else if (cornFreq < 2000) {
        cornFreq *= 1.5;
    } else if (cornFreq < 15000) {
        cornFreq = Math.floor(cornFreq/1000.0 + 1) * 1000;
    } else {
        cornFreq = Math.floor(cornFreq/1000.0 + 5) * 1000;
    }
    cornFreqChanged();
}
function decCornFreq() {
    if (cornFreq == -1) {
        cornFreq = 4000;
    } else if (cornFreq < 2000) {
        cornFreq *= 0.75;
    } else if (cornFreq < 15000) {
        cornFreq = Math.ceil(cornFreq/1000.0 - 1) * 1000;
    } else {
        cornFreq = Math.ceil(cornFreq/1000.0 - 5) * 1000;
    }
    cornFreqChanged();
}

function cornFreqChanged() {
    $.cookie('corns', cornFreq);
    startCorns();
}
function nameCornFreq() {
    if (cornFreq == -1) {
        s = "never";
    } else {
        s = "[" + (cornFreq/1000.0).toFixed(2) + "]";
    }
    $('#cornFreq').html(s);
}

$(function() { startCorns(); });


function getCorns() {
    return $('div img[src*="cornify.com/getacorn.php"]')
                .map(function() { return this.parentElement });
}

function slaughterCorns() {
    getCorns().remove();
}

function cornDancer(startLeft, startTop, endLeft, endTop, amp, steps, periods) {
    // we move along a sine curve which has been translated/rotated to
    // be on the (start -> end) line

    // this function returns another function which takes an int, which is a
    // step number in [0, steps), and updates the unicorn position

    // all variables are in percent-of-the-page space

    // if start is undefined, we default to 2%, 80%
    if (typeof(startLeft) == 'undefined') { startLeft = 2; }
    if (typeof(startTop)  == 'undefined') { startTop = 60; }

    // if end is undefined, default to 98%, 80%
    if (typeof(endLeft) == 'undefined') { endLeft = 75; }
    if (typeof(endTop)  == 'undefined') { endTop = 60; }

    // sine argument defaults
    if (typeof(amp) == 'undefined') { amp = 5; }
    if (typeof(steps) == 'undefined') { steps = 1000; }
    if (typeof(periods) == 'undefined') { periods = 5; }

    // x, y represent distance in the sine-curve basis (origin at start-point)
    // X, Y are actual page positions

    // various properties of the start->end line
    DX = 1.0 * endLeft - startLeft;
    DY = 1.0 * endTop - startTop;

    length = Math.sqrt(DY*DY + DX*DX);
    slope = DY / DX

    cos_th = DX / length;
    sin_th = DY / length;

    // dance, unicorn, dance!
    return function(i) {
        x = 1.0 * i / steps * Math.abs(DX);
        y = amp * Math.sin(x/DX * 2 * periods * Math.PI);

        X = startLeft + x*cos_th - y*sin_th;
        Y = startTop  + x*sin_th + y*cos_th;

        return [ X, Y ];
    }
}


function placeCorn(corn, x, y) {
    corn.style.left = x + "%";
    corn.style.top  = y + "%";
}

function danceCorn(corn, callback, delay,
               startLeft, startTop, endLeft, endTop, amp, steps, periods) {

    if (typeof(delay) == 'undefined') { delay = 20; }
    d = cornDancer(startLeft, startTop, endLeft, endTop, amp, steps, periods);

    function makeDance(i, dancer) {
        if (i < steps) {
            a = dancer(i);
            placeCorn(corn, a[0], a[1]);
            setTimeout(function() { makeDance(i+1, dancer) }, delay);
        } else {
            if (typeof(callback) != 'undefined') {
                callback();
            }
        }
    }
    makeDance(0, d);
}


function danceRight(corn, speed, amp, periods) {
    if (typeof(speed  ) == 'undefined') { speed   = 15; }
    if (typeof(amp    ) == 'undefined') { amp     =  4; }
    if (typeof(periods) == 'undefined') { periods =  10; }

    height = 65; // Math.random() * 60 + 10
    danceCorn(corn, function() { $(corn).remove(); },
              speed, -15, height, 102, height, amp, 1000, periods);
}
function danceLeft(corn, speed, amp, periods) {
    if (typeof(speed  ) == 'undefined') { speed   = 15; }
    if (typeof(amp    ) == 'undefined') { amp     =  3; }
    if (typeof(periods) == 'undefined') { periods =  15; }

    height = 65; // Math.random() * 60 + 10
    danceCorn(corn, function() { $(corn).remove(); },
              speed, 102, height, -30, height, amp, 1000, periods);
}
function dancePast(corn, speed, amp, periods) {
    f = (Math.random() > 10.5) ? danceRight : danceLeft;
    f(corn, speed, amp, periods);
}

function makeCorn() {
    oldList = getCorns();
    cornify_add();
    newList = getCorns();
    for (var i = 0; i < newList.length; i++) {
        if (oldList.index(newList[i]) == -1) {
            return newList[i];
        }
    }
}

function makeCornDancer(speed, amp, periods) {
    corn = makeCorn();
    dancePast(corn, speed, amp, periods);
}
