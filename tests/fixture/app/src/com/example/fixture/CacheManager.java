package com.example.fixture;

import android.content.Context;

/** TEST CASE 3 - third class exposing a "refresh" method (nameExact must return several hits). */
public class CacheManager {

    public void refresh() {
        // deliberately empty
    }

    public void clear(Context context) {
        StateWriter.updateBySilent(context, 0);
    }
}
