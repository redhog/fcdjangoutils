var fcdjangoutils = {

};

String.prototype.format = function(){
    var res = "";
    var aIdx = 0;

    var idx = 0;

    while(idx < this.length){
	switch(this[idx]){
	case '%':
	    switch(this[idx+1]){
	    case '%':
		res += '%';
		idx+=2;
		break;
	    case 's':
		res += (new String(arguments[aIdx++])).toString();
		idx+=2;
		break;

	    case '(':
		var end = this.indexOf(')', idx);
		if(end == -1)
		    throw "Invalid format string";

		var name = this.substr(idx+2, end-idx-2);
		console.log('name is');
		console.log(name);
		idx = end+1;
		switch(this[idx]){
		case 's':
		    res += (new String(arguments[0][name])).toString();
		    idx++;
		    break;

		default:
		    throw "Unsupported format option: '" + this[idx] + "'";

		}
		break;
	    default:
		throw "Unsupported format option: '" + this[idx+1] + "'";
	    }
	    break;

	default:
	    res += this[idx];
	    idx++;
	    break;
	}
    }

    return res;
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
