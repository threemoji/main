package com.threemoji.threemoji;

import com.threemoji.threemoji.data.ChatContract;

import android.content.Context;
import android.content.Intent;
import android.database.Cursor;
import android.os.Bundle;
import android.support.annotation.Nullable;
import android.support.v4.app.Fragment;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.util.Log;
import android.util.TypedValue;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class ChatListFragment extends Fragment {

    private static final String TAG = ChatListFragment.class.getSimpleName();

    private final String[] CHAT_ITEM_PROJECTION = new String[]{
            ChatContract.PartnerEntry.COLUMN_UUID,
            ChatContract.PartnerEntry.COLUMN_EMOJI_1,
            ChatContract.PartnerEntry.COLUMN_EMOJI_2,
            ChatContract.PartnerEntry.COLUMN_EMOJI_3,
            ChatContract.PartnerEntry.COLUMN_GENDER,
            ChatContract.PartnerEntry.COLUMN_GENERATED_NAME,
    };

    // ================================================================
    // Methods for initialising the components of the chat list
    // ================================================================
    @Nullable
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        RecyclerView rv = (RecyclerView) inflater.inflate(
                R.layout.fragment_chat_list, container, false);
        setupRecyclerView(rv);
        return rv;
    }

    private void setupRecyclerView(RecyclerView recyclerView) {
        ArrayList<ChatItem> chats = new ArrayList<ChatItem>();

//        ContentValues testValues = new ContentValues();

//        testValues.put(ChatContract.PartnerEntry.COLUMN_UUID, "1d0982b4-4a73-41b1-b220-052667e223c2");
//        testValues.put(ChatContract.PartnerEntry.COLUMN_EMOJI_1, "emoji_1f604");
//        testValues.put(ChatContract.PartnerEntry.COLUMN_EMOJI_2, "emoji_1f603");
//        testValues.put(ChatContract.PartnerEntry.COLUMN_EMOJI_3, "emoji_1f600");
//        testValues.put(ChatContract.PartnerEntry.COLUMN_GENDER, "FEMALE");
//        testValues.put(ChatContract.PartnerEntry.COLUMN_GENERATED_NAME, "Weepy Xoni");

//        SharedPreferences prefs = PreferenceManager.getDefaultSharedPreferences(getActivity());
//        testValues.put(ChatContract.PartnerEntry.COLUMN_UUID, prefs.getString(getString(R.string.profile_uid_key), ""));
//        testValues.put(ChatContract.PartnerEntry.COLUMN_EMOJI_1, prefs.getString(getString(R.string.profile_emoji_one_key), ""));
//        testValues.put(ChatContract.PartnerEntry.COLUMN_EMOJI_2, prefs.getString(getString(R.string.profile_emoji_two_key), ""));
//        testValues.put(ChatContract.PartnerEntry.COLUMN_EMOJI_3, prefs.getString(getString(R.string.profile_emoji_three_key), ""));
//        testValues.put(ChatContract.PartnerEntry.COLUMN_GENDER, prefs.getString(getString(R.string.profile_gender_key), ""));
//        testValues.put(ChatContract.PartnerEntry.COLUMN_GENERATED_NAME, prefs.getString(getString(R.string.profile_generated_name_key), ""));
//
//        Uri uri = getActivity().getContentResolver()
//                  .insert(ChatContract.PartnerEntry.CONTENT_URI, testValues);
//        Log.v(TAG, uri.toString());

//        int rowsDeleted = getActivity().getContentResolver().delete(ChatContract.PartnerEntry.CONTENT_URI,
//                                                                    ChatContract.PartnerEntry.COLUMN_GENERATED_NAME + " = ?",
//                                                                    new String[] {"Shiny Boubou"});
//        Log.v(TAG, rowsDeleted+"");

        Cursor cursor = getActivity().getContentResolver()
                                     .query(ChatContract.PartnerEntry.CONTENT_URI,
                                            CHAT_ITEM_PROJECTION, null, null, null);
//        addDummyData(chats);
        if (cursor != null) {
            while (cursor.moveToNext()) {
                chats.add(
                        new ChatItem(
                                cursor.getString(0),
                                cursor.getString(1),
                                cursor.getString(2),
                                cursor.getString(3),
                                cursor.getString(4),
                                cursor.getString(5),
                                getRandomTime()));
            }
        }

        recyclerView.setLayoutManager(new LinearLayoutManager(recyclerView.getContext()));
        recyclerView.setAdapter(new RecyclerViewAdapter(getActivity(), chats));
    }

    private String getRandomTime() {
        Random rand = new Random();
        return rand.nextInt(60) + " minutes ago";
    }


    // ================================================================
    // Inner class to represent each row of the chat list
    // ================================================================
    public class ChatItem {
        public String uuid;
        public String emoji1;
        public String emoji2;
        public String emoji3;
        public String gender;
        public String partnerName;
        public String lastActivity;

        public ChatItem(String uuid, String emoji1, String emoji2, String emoji3, String gender,
                        String partnerName, String lastActivity) {
            this.uuid = uuid;
            this.emoji1 = emoji1;
            this.emoji2 = emoji2;
            this.emoji3 = emoji3;
            this.gender = gender;
            this.partnerName = partnerName;
            this.lastActivity = lastActivity;
        }
    }


    // ================================================================
    // Inner class to handle the population of items in the list
    // ================================================================
    public static class RecyclerViewAdapter
            extends RecyclerView.Adapter<RecyclerViewAdapter.ViewHolder> {

        private List<ChatItem> mItems;
        private final TypedValue mTypedValue = new TypedValue();
        private int mBackground;
        private Context mContext;

        public RecyclerViewAdapter(Context context, List<ChatItem> items) {
            // Initialises the animated background of the each list item.
            context.getTheme().resolveAttribute(R.attr.selectableItemBackground, mTypedValue, true);
            mBackground = mTypedValue.resourceId;
            mContext = context;
            mItems = items;
        }

        @Override
        public ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
            View view = LayoutInflater.from(parent.getContext())
                                      .inflate(R.layout.item_chat_list, parent, false);

            // Sets the animated background of each list item to show when item is touched.
            view.setBackgroundResource(mBackground);

            return new ViewHolder(view);
        }

        @Override
        public void onBindViewHolder(final ViewHolder holder, int position) {
            final ChatItem currentItem = mItems.get(position);
            holder.emoji1.setImageResource(mContext.getResources().getIdentifier(currentItem.emoji1, "drawable", mContext.getPackageName()));
            holder.emoji2.setImageResource(mContext.getResources().getIdentifier(currentItem.emoji2, "drawable", mContext.getPackageName()));
            holder.emoji3.setImageResource(mContext.getResources().getIdentifier(currentItem.emoji3, "drawable", mContext.getPackageName()));
            holder.partnerName.setText(currentItem.partnerName);
            holder.lastActivity.setText(currentItem.lastActivity);

            holder.view.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    Context context = v.getContext();
                    Intent intent = new Intent(context, ChatActivity.class);
                    intent.putExtra("action", ChatActivity.Action.DISPLAY.name());
                    intent.putExtra("uuid", currentItem.uuid);
                    intent.putExtra("emoji_1", currentItem.emoji1);
                    intent.putExtra("emoji_2", currentItem.emoji2);
                    intent.putExtra("emoji_3", currentItem.emoji3);
                    intent.putExtra("gender", currentItem.gender);
                    intent.putExtra("generated_name", currentItem.partnerName);
                    context.startActivity(intent);

                    Log.d(TAG, holder.partnerName.getText().toString());
                }
            });
        }

        @Override
        public int getItemCount() {
            return mItems.size();
        }


        // ================================================================
        // Inner class to represent ChatItems in actual views
        // ================================================================
        public static class ViewHolder extends RecyclerView.ViewHolder {
            public final View view;
            public final ImageView emoji1;
            public final ImageView emoji2;
            public final ImageView emoji3;
            public final TextView partnerName;
            public final TextView lastActivity;

            public ViewHolder(View view) {
                super(view);
                this.view = view;
                emoji1 = (ImageView) view.findViewById(R.id.emoji1);
                emoji2 = (ImageView) view.findViewById(R.id.emoji2);
                emoji3 = (ImageView) view.findViewById(R.id.emoji3);
                partnerName = (TextView) view.findViewById(R.id.partnerName);
                lastActivity = (TextView) view.findViewById(R.id.lastActivity);
            }
        }
    }
}
