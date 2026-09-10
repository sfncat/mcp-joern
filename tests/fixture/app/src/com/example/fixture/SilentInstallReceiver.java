package com.example.fixture;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/** TEST CASE 2b - anonymous inner class (compiles to SilentInstallReceiver$1) carrying a call. */
public class SilentInstallReceiver extends BroadcastReceiver {

    @Override
    public void onReceive(final Context context, Intent intent) {
        Runnable task = new Runnable() {                          // -> SilentInstallReceiver$1
            @Override
            public void run() {
                StateWriter.updateBySilent(context, 1);
            }
        };
        task.run();
    }
}
