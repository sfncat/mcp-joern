package com.example.fixture;

import android.content.Context;
import android.content.Intent;
import android.util.Log;

/**
 * TEST CASE 1/2/3 - the business entry point is handleBroadCastReceive() (not onReceive),
 * it starts a 4-hop delegation chain, and refresh() is a deliberately duplicated
 * simple method name.
 */
public class AccountReceiver extends SafeReceiverBase {

    private final HdMemberManager manager = new HdMemberManager();

    @Override
    public void handleBroadCastReceive(Context context, Intent intent) {
        String action = intent.getAction();
        Log.d("AccountReceiver", "onReceive action : " + action);
        if (Constants.ACTION_REMOVE_ACCOUNT.equals(action)) {
            manager.call(context);                       // hop 1
        } else if (Constants.ACTION_LOGIN_SUCCESS.equals(action)) {
            manager.call(context);
        }
    }

    /** TEST CASE 3 - duplicated simple name (see CacheManager.refresh, HdMemberManager.refresh). */
    public void refresh() {
        manager.call(null);
    }
}
