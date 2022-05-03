odoo.define('alpamire.ClientActionExtended', function (require) {
'use strict';

    var ClientActionExtended = require('stock_barcode.ClientAction');

    ClientActionExtended.include({

        _isOptionalButtonsEnabled: function () {
            return false;
        },

//        _step_product: function (barcode, linesActions) {
//        var self = this;
//        this.currentStep = 'product';
//        this.stepState = $.extend(true, {}, this.currentState);
//        var errorMessage;
//        var product = this._isProduct(barcode);
//        if (product) {
//            if (product.tracking !== 'none') {
//                this.currentStep = 'lot';
//            }
//            var res = this._incrementLines({'product': product, 'barcode': barcode});
//            console.log('res', res)
//            if (res.isNewLine) {
//                if (this.actionParams.model === 'stock.inventory') {
//                    // FIXME sle: add owner_id, prod_lot_id, owner_id, product_uom_id
//                    return this._rpc({
//                        model: 'product.product',
//                        method: 'get_theoretical_quantity',
//                        args: [
//                            res.lineDescription.product_id.id,
//                            res.lineDescription.location_id.id,
//                        ],
//                    }).then(function (theoretical_qty) {
//                        res.lineDescription.theoretical_qty = theoretical_qty;
//                        linesActions.push([self.linesWidget.addProduct, [res.lineDescription, self.actionParams.model]]);
//                        self.scannedLines.push(res.id || res.virtualId);
//                        return Promise.resolve({linesActions: linesActions});
//                    });
//                } else {
//                    linesActions.push([this.linesWidget.addProduct, [res.lineDescription, this.actionParams.model]]);
//                }
//            } else if (!(res.id || res.virtualId)) {
//                return Promise.reject(_("There are no lines to increment."));
//            } else {
//                if (product.tracking === 'none') {
////OVERRIDE FOR MULTI INNER PACKAGE
//                    console.log('product', product.default_code)
//                    linesActions.push([this.linesWidget.incrementProduct, [res.id || res.virtualId, product.qty || (1 * product.default_code), this.actionParams.model]]);
//                } else {
//                    linesActions.push([this.linesWidget.incrementProduct, [res.id || res.virtualId, 0, this.actionParams.model]]);
//                }
//            }
//            this.scannedLines.push(res.id || res.virtualId);
//            return Promise.resolve({linesActions: linesActions});
//        } else {
//            var success = function (res) {
//                return Promise.resolve({linesActions: res.linesActions});
//            };
//            var fail = function (specializedErrorMessage) {
//                self.currentStep = 'product';
//                if (specializedErrorMessage){
//                    return Promise.reject(specializedErrorMessage);
//                }
//                if (! self.scannedLines.length) {
//                    if (self.groups.group_tracking_lot) {
//                        errorMessage = _t("You are expected to scan one or more products or a package available at the picking's location");
//                    } else {
//                        errorMessage = _t('You are expected to scan one or more products.');
//                    }
//                    return Promise.reject(errorMessage);
//                }
//
//                var destinationLocation = self.locationsByBarcode[barcode];
//                if (destinationLocation) {
//                    return self._step_destination(barcode, linesActions);
//                } else {
//                    errorMessage = _t('You are expected to scan more products or a destination location.');
//                    return Promise.reject(errorMessage);
//                }
//            };
//            return self._step_lot(barcode, linesActions).then(success, function () {
//                return self._step_package(barcode, linesActions).then(success, fail);
//            });
//        }
//    },


    });
});