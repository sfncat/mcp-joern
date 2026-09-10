package com.example.fixture;

import android.content.Context;
import java.util.ArrayList;
import java.util.List;

/** hop 1 of the delegation chain; also carries framework (JDK) calls that the chain tool must skip. */
public class HdMemberManager {

    private final List<Callback> callbacks = new ArrayList<Callback>();

    public HdMemberManager() {
        callbacks.add(new MemberCallback());
    }

    public void call(Context context) {                          // hop 1
        for (int i = 0; i < callbacks.size(); i++) {             // JDK calls -> skipped by chain tool
            Callback callback = callbacks.get(i);
            if (callback != null) {
                callback.onAccountQuit(context);                 // hop 2
            }
        }
    }

    /** TEST CASE 3 - duplicated simple name. */
    public void refresh() {
        call(null);
    }
}
