$(function() {
	$('textarea[max-rows]').each(function () {
		var textarea = $(this);

		var minRows = Number(textarea.attr('rows'));
		var maxRows = Number(textarea.attr('max-rows'));

		// clone the textarea and hide it offscreen
		// TODO: copy all the styles
		var textareaClone = $('<textarea/>', {
			rows: minRows,
			maxRows: maxRows,
			class: textarea.attr('class')
		}).css({
			position: 'absolute',
			left: -$(document).width() * 2
		}).insertAfter(textarea);

		var textareaCloneNode = textareaClone.get(0);

		textarea.on('input', function () {
			// copy the input from the real textarea
			textareaClone.val(textarea.val());

			// set as small as possible to get the real scroll height
			textareaClone.attr('rows', 1);

			// save the real scroll height
			var scrollHeight = textareaCloneNode.scrollHeight;

			// increase the number of rows until the content fits
			for (var rows = minRows; rows < maxRows; rows++) {
				textareaClone.attr('rows', rows);

				if (textareaClone.height() > scrollHeight) {
					break;
				}
			}

			// copy the rows value back to the real textarea
			textarea.attr('rows', textareaClone.attr('rows'));
		}).trigger('input');
	});
});