var fcdjangoutils = {

};

fcdjangoutils.message = function(msg, id, style){
    style = style || 'message';
    var lst = $('#messages');
    var line = $('<li>').text(msg).addClass(style);
    if(id) {
	$('#' + id, lst).detach();
	line.attr('id', id);
    }
    lst.append(line);
}

fcdjangoutils.error = function(msg, id){
    fcdjangoutils.message(msg,id, 'error');
}

fcdjangoutils.warning = function(msg, id){
    fcdjangoutils.message(msg, id, 'warning');
}

fcdjangoutils.fromIsoDate = function(txt){
    var darr = txt.split("-");
    if(darr.length != 3)
	return null;
    // Input is iso date, but javascript expects
    // month component in range 0..11,
    // so we subtract one from the month
    darr[1]-= 1;
    return new Date(Date.UTC.apply(null, darr));
};

fcdjangoutils.toIsoDate = function (date){
    return "" + date.getFullYear() + "-" + (date.getMonth()+1)+"-" + date.getDate();
}

/* Make sure the application works even if console debugging is used without an active Firebug. */
if(typeof(console) === 'undefined') {
    var console = {}
    console.log = console.error = console.info = console.debug = console.warn = console.trace = console.dir = console.dirxml = console.group = console.groupEnd = console.time = console.timeEnd = console.assert = console.profile = function() {};
}
