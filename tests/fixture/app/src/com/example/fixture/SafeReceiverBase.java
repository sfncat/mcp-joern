package com.example.fixture;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/**
 * TEST CASE 1 - custom base receiver.
 *
 * onReceive() lives here and only forwards to handleBroadCastReceive(), which the
 * subclass implements. Tooling that reads only the "onReceive" body sees an empty
 * shell and misses the whole business logic (the NO-onReceive shell problem).
 */
public abstract class SafeReceiverBase extends BroadcastReceiver {

    @Override
    public final void onReceive(Context context, Intent intent) {
        handleBroadCastReceive(context, intent);
    }

    public abstract void handleBroadCastReceive(Context context, Intent intent);
}
