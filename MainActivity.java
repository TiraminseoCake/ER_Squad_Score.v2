package com.example.myapplication;

import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

public class MainActivity extends AppCompatActivity {

    private DatabaseReference databaseReference;
    private EditText inputCharacter;
    private Button btnFetch;
    private TextView recommendationsView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        inputCharacter = findViewById(R.id.inputCharacter);
        btnFetch = findViewById(R.id.btnFetch);
        recommendationsView = findViewById(R.id.recommendationsView);

        // Firebase Database Reference
        databaseReference = FirebaseDatabase.getInstance().getReference("recommendations");

        // 버튼 클릭 이벤트
        btnFetch.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String characterName = inputCharacter.getText().toString().trim();
                if (!characterName.isEmpty()) {
                    fetchRecommendations(characterName);
                } else {
                    recommendationsView.setText("실험체 이름을 입력해주세요.");
                }
            }
        });
    }

    private void fetchRecommendations(String characterName) {
        DatabaseReference characterRef = databaseReference.child(characterName);

        // 데이터 읽기
        characterRef.addValueEventListener(new ValueEventListener() {
            @Override
            public void onDataChange(@NonNull DataSnapshot snapshot) {
                if (snapshot.exists()) {
                    StringBuilder recommendations = new StringBuilder();
                    for (DataSnapshot data : snapshot.getChildren()) {
                        recommendations.append(data.getKey())
                                .append(": ")
                                .append(data.getValue(String.class))
                                .append("\n");
                    }
                    recommendationsView.setText(recommendations.toString());
                } else {
                    recommendationsView.setText("해당 실험체에 대한 추천 조합이 없습니다.");
                }
            }

            @Override
            public void onCancelled(@NonNull DatabaseError error) {
                Log.e("FirebaseError", "Failed to read data", error.toException());
                recommendationsView.setText("데이터를 불러오는 중 오류가 발생했습니다.");
            }
        });
    }
}