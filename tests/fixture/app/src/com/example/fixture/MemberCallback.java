package com.example.fixture;

import android.content.Context;

/** hop 2 of the delegation chain. */
public class MemberCallback implements Callback {

    @Override
    public void onAccountQuit(Context context) {
        StateWriter.updateBySilent(context, 2);                  // hop 3
    }
}
