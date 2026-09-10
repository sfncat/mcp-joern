package com.example.fixture;

import android.content.Context;

/** interface hop of the chain (interface -> implementation dispatch). */
public interface Callback {

    void onAccountQuit(Context context);
}
