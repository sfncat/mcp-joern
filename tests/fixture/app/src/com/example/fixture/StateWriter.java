package com.example.fixture;

import android.content.Context;
import android.content.SharedPreferences;

/**
 * TEST CASE 4 - the business write at the end of the chain. Mirrors hms.location's
 * "hd_member" SharedPreferences write, i.e. the marker the chain tool must surface.
 */
public final class StateWriter {

    private StateWriter() {
    }

    public static void updateBySilent(Context context, int state) {          // hop 3
        SharedPreferences prefs = context.getSharedPreferences(
                "hd_member_store", Context.MODE_PRIVATE);
        prefs.edit().putInt("hd_member", state).apply();                     // <- business write
    }
}
