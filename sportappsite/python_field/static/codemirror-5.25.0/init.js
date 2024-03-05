(function(){
    var $ = django.jQuery;
    $(document).ready(function(){

        $("textarea.python-code").each(function(idx, el){
            cm = CodeMirror.fromTextArea(el, {

                lineNumbers: true,
                mode: 'python',
		lineSeparator: '\n',
		indentUnit: 4,
		matchBrackets: true,
		styleActiveLine: true,
		autoCloseBrackets: true,
		showTrailingSpace: true,
		lineWrapping: true,
		gutters: [
		    "CodeMirror-foldgutter",
		    "CodeMirror-linenumbers"
		],
		foldGutter: {
                    rangeFinder: new CodeMirror.fold.combine(
			CodeMirror.fold.brace,
			CodeMirror.fold.comment,
		        CodeMirror.fold.indent
		    )},

		foldGutter: true,
		foldCode: true,
		styleSelectedText: true,
		theme: 'eclipse',

            });
	    cm.setSize(780, 'auto');
	    cm.getWrapperElement().style["font-size"] = "10px";
	    cm.refresh();
	});
    });
})();
