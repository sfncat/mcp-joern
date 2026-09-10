package com.example.fixture;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/** TEST CASE 7 - permission-gated receiver (manifest declares a signature-level permission). */
public class GatedReceiver extends BroadcastReceiver {

    @Override
    public void onReceive(Context context, Intent intent) {
        if (Constants.ACTION_GATED.equals(intent.getAction())) {
            StateWriter.updateBySilent(context, 3);
        }
    }
}
