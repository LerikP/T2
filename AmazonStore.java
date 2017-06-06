package org.renpy.iap;

import java.util.HashSet;
import java.util.Map;

import android.app.Activity;

public class AmazonStore extends Store implements PurchasingListener {

    Activity activity = null;

    boolean finished = true;


    public AmazonStore(Activity activity) {
        this.activity = activity;
    }

    @Override
    public void destroy() {
    }

    @Override
    public boolean getFinished() {
        return finished;
    }

    @Override
    public String getStoreName() {
        return "amazon";
    }

    @Override
    public void updatePrices() {
        HashSet<String> skuset = new HashSet<String>(skus);

        finished = false;
    }

    @Override
    public void restorePurchases() {
        finished = false;
    }

    @Override
    public void beginPurchase(String sku) {
        finished = false;
    }


    @Override
    public void onUserDataResponse(final String response) {
    }

    @Override
    public void onPurchaseUpdatesResponse(final String response) {
        finished = false;
    }

    @Override
    public void onPurchaseResponse(final String response) {
        finished = true;
    }

    @Override
    public void onProductDataResponse(String response) {
        finished = true;
    }

}
