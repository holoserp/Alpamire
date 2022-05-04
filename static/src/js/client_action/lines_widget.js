odoo.define('alpamire.lines_widget', function (require) {
'use strict';

var LinesWidget = require('stock_barcode.LinesWidget');

var LinesWidgetExt = LinesWidget.include({

    _highlightLine: function ($line, doNotClearLineHighlight) {
        var $body = this.$el.filter('.o_barcode_lines');
        if (! doNotClearLineHighlight) {
            this.clearLineHighlight();
        }
        // Highlight `$line`.
        $line.toggleClass('o_highlight', true);
        $line.parents('.o_barcode_lines').toggleClass('o_js_has_highlight', true);

        var isReservationProcessed;
        if ($line.find('.o_barcode_scanner_qty').text().indexOf('/') === -1) {
            if (this.isPickingRelated && !this.isImmediatePicking) {
                isReservationProcessed = 1;  // product not part of initial transfer
            } else {
                isReservationProcessed = false; // there are no initial transfer products
            }
        } else {
            isReservationProcessed = this._isReservationProcessedLine($line);
        }
        if (isReservationProcessed === 1) {
            $line.toggleClass('o_highlight_green', false);
            $line.toggleClass('o_highlight_red', true);
        } else {
            $line.toggleClass('o_highlight_green', true);
            $line.toggleClass('o_highlight_red', false);
            if ($line.attr('data-picking-id')) {
                // determine picking specific color dynamically since border-color is set in template
                // we must use a more specific css value than 'border-color' for firefox for some reason
                $line.css("box-shadow", "inset 0px 0px 0px 3px " +  $line.css('border-top-color'));
            }
        }

        // don't move to done lines since they're at the bottom of list
        if (!$line.hasClass('o_line_completed')) {
            // Scroll to `$line`.
            $body.animate({
                scrollTop: $body.scrollTop() + $line.position().top - $body.height()/2 + $line.height()/2
            }, 500);
        }
    },

    _highlightNextExpected: function(message) {
        if (message != 'scan_lot') {
            this.$('.o_next_expected').removeClass('o_next_expected');
            if (! this._isReservationProcessed()) {
                const $lines = this.$('.o_barcode_line:not(.o_line_qty_completed)');
                for (const line of $lines) {
                    // do not include lines not part of original picking as "next_expected"
                    if ($(line).find('.o_barcode_scanner_qty').text().indexOf('/') != -1) {
                        $(line).find('.fa-tags').addClass('o_next_expected');
                        break;
                    }
                }
            }
        }
    },


});

return LinesWidgetExt;

});