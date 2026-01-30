import React, { useEffect, useState } from "react";
import { Image, Linking, SafeAreaView, ScrollView, Text, TextInput, TouchableOpacity, View } from "react-native";
import * as DocumentPicker from "expo-document-picker";
import * as ImagePicker from "expo-image-picker";

type TabKey = "home" | "learn" | "practice" | "exam" | "report" | "profile";

const API_BASE = "http://localhost:28000";

const tabs: { key: TabKey; label: string }[] = [
  { key: "home", label: "首页" },
  { key: "learn", label: "学习" },
  { key: "practice", label: "练习" },
  { key: "exam", label: "考试" },
  { key: "report", label: "报告" },
  { key: "profile", label: "我的" },
];

const cardStyle = {
  backgroundColor: "#ffffff",
  borderRadius: 16,
  padding: 16,
  marginBottom: 12,
};

export default function App() {
  const [tab, setTab] = useState<TabKey>("home");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");
  const [status, setStatus] = useState("");
  const [word, setWord] = useState<any>(null);
  const [imageUrlInput, setImageUrlInput] = useState("");
  const [audioUrlInput, setAudioUrlInput] = useState("");
  const [mediaStatus, setMediaStatus] = useState("");
  const [adminToken, setAdminToken] = useState("");

  const login = async () => {
    if (!email || !password) {
      setStatus("请输入邮箱与密码");
      return;
    }
    try {
      const res = await fetch("http://localhost:28000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "登录失败");
      }
      const data = await res.json();
      setToken(data.access_token);
      setStatus("登录成功");
    } catch (err: any) {
      setStatus(err.message || "登录失败");
    }
  };

  const loadWord = async () => {
    try {
      const res = await fetch(`${API_BASE}/words?limit=1&skip=0`);
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "加载失败");
      }
      const data = await res.json();
      const item = data.items ? data.items[0] : data[0];
      if (item) {
        setWord(item);
        setImageUrlInput(item.image_url || "");
        setAudioUrlInput(item.audio_url || "");
      }
    } catch (err: any) {
      setMediaStatus(err.message || "加载失败");
    }
  };

  const saveMedia = async () => {
    if (!word?.id) {
      setMediaStatus("未加载到单词");
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/words/${word.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image_url: imageUrlInput, audio_url: audioUrlInput }),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "保存失败");
      }
      const data = await res.json();
      setWord(data);
      setMediaStatus("已绑定媒体链接");
    } catch (err: any) {
      setMediaStatus(err.message || "保存失败");
    }
  };

  useEffect(() => {
    loadWord();
  }, []);

  const uploadMedia = async (kind: "image" | "audio", file: { uri: string; name?: string; mimeType?: string }) => {
    if (!adminToken) {
      setMediaStatus("请输入管理员 Token");
      return;
    }
    if (!word?.id) {
      setMediaStatus("未加载到单词");
      return;
    }
    const form = new FormData();
    form.append("kind", kind);
    form.append("file", {
      uri: file.uri,
      name: file.name || `upload-${Date.now()}`,
      type: file.mimeType || (kind === "image" ? "image/png" : "audio/mpeg"),
    } as any);
    setMediaStatus("上传中...");
    const res = await fetch(`${API_BASE}/admin/media/upload`, {
      method: "POST",
      headers: { "X-Admin-Token": adminToken },
      body: form,
    });
    if (!res.ok) {
      const text = await res.text();
      setMediaStatus(text || "上传失败");
      return;
    }
    const data = await res.json();
    const field = kind === "image" ? "image_url" : "audio_url";
    await fetch(`${API_BASE}/words/${word.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ [field]: data.url }),
    });
    if (kind === "image") {
      setImageUrlInput(data.url);
    } else {
      setAudioUrlInput(data.url);
    }
    setMediaStatus("上传并绑定成功");
    loadWord();
  };

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: false,
      quality: 0.9,
    });
    if (!result.canceled && result.assets?.[0]) {
      const asset = result.assets[0];
      await uploadMedia("image", { uri: asset.uri, name: asset.fileName, mimeType: asset.mimeType });
    }
  };

  const pickAudio = async () => {
    const result = await DocumentPicker.getDocumentAsync({ type: "audio/*", copyToCacheDirectory: true });
    if (!result.canceled && result.assets?.[0]) {
      const asset = result.assets[0];
      await uploadMedia("audio", { uri: asset.uri, name: asset.name, mimeType: asset.mimeType });
    }
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#F4F6FB" }}>
      <View style={{ padding: 16 }}>
        <Text style={{ fontSize: 24, fontWeight: "700", color: "#0B1B2B" }}>English Learning</Text>
        <Text style={{ color: "#5B6B7B", marginTop: 6 }}>移动端流程预览</Text>
      </View>

      <ScrollView style={{ padding: 16 }}>
        {tab === "home" && (
          <View style={cardStyle}>
            <Text style={{ fontSize: 18, fontWeight: "600" }}>今日目标</Text>
            <Text style={{ marginTop: 6, color: "#5B6B7B" }}>学习 20 · 练习 8 · 考试 1</Text>
          </View>
        )}

        {tab === "learn" && (
          <View style={{ gap: 12 }}>
            <View style={cardStyle}>
              <Text style={{ fontSize: 18, fontWeight: "600" }}>单词：{word?.text || "加载中..."}</Text>
              <Text style={{ marginTop: 8 }}>释义：{word?.meaning || "-"}</Text>
              <Text style={{ marginTop: 8, color: "#5B6B7B" }}>{word?.example || ""}</Text>
            </View>
            <View style={cardStyle}>
              <Text style={{ fontSize: 16, fontWeight: "600" }}>图片预览</Text>
              {word?.image_url ? (
                <Image
                  source={{ uri: word.image_url }}
                  style={{ height: 180, borderRadius: 12, marginTop: 10 }}
                  resizeMode="cover"
                />
              ) : (
                <Text style={{ marginTop: 8, color: "#5B6B7B" }}>未绑定图片</Text>
              )}
            </View>
            <View style={cardStyle}>
              <Text style={{ fontSize: 16, fontWeight: "600" }}>音频预览</Text>
              {word?.audio_url ? (
                <TouchableOpacity style={{ marginTop: 10 }} onPress={() => Linking.openURL(word.audio_url)}>
                  <Text style={{ color: "#1F6BFF" }}>播放音频</Text>
                </TouchableOpacity>
              ) : (
                <Text style={{ marginTop: 8, color: "#5B6B7B" }}>未绑定音频</Text>
              )}
            </View>
            <View style={cardStyle}>
              <Text style={{ fontSize: 16, fontWeight: "600" }}>绑定媒体链接</Text>
              <Text style={{ marginTop: 6, color: "#5B6B7B" }}>移动端建议从后台上传后粘贴链接</Text>
              <TextInput
                style={{ marginTop: 12, backgroundColor: "#F1F5F9", padding: 10, borderRadius: 10 }}
                placeholder="image_url"
                value={imageUrlInput}
                onChangeText={setImageUrlInput}
              />
              <TextInput
                style={{ marginTop: 8, backgroundColor: "#F1F5F9", padding: 10, borderRadius: 10 }}
                placeholder="audio_url"
                value={audioUrlInput}
                onChangeText={setAudioUrlInput}
              />
              <TouchableOpacity style={{ marginTop: 10 }} onPress={saveMedia}>
                <Text style={{ color: "#1F6BFF" }}>保存绑定</Text>
              </TouchableOpacity>
              <Text style={{ marginTop: 8, color: "#5B6B7B" }}>{mediaStatus}</Text>
            </View>
            <View style={cardStyle}>
              <Text style={{ fontSize: 16, fontWeight: "600" }}>管理员上传（Expo）</Text>
              <Text style={{ marginTop: 6, color: "#5B6B7B" }}>需要安装 expo-image-picker / expo-document-picker</Text>
              <TextInput
                style={{ marginTop: 12, backgroundColor: "#F1F5F9", padding: 10, borderRadius: 10 }}
                placeholder="X-Admin-Token"
                value={adminToken}
                onChangeText={setAdminToken}
              />
              <TouchableOpacity style={{ marginTop: 10 }} onPress={pickImage}>
                <Text style={{ color: "#1F6BFF" }}>选择图片并上传</Text>
              </TouchableOpacity>
              <TouchableOpacity style={{ marginTop: 10 }} onPress={pickAudio}>
                <Text style={{ color: "#1F6BFF" }}>选择音频并上传</Text>
              </TouchableOpacity>
              <Text style={{ marginTop: 8, color: "#5B6B7B" }}>{mediaStatus}</Text>
            </View>
          </View>
        )}

        {tab === "practice" && (
          <View style={cardStyle}>
            <Text style={{ fontSize: 18, fontWeight: "600" }}>练习：图片选义</Text>
            <Text style={{ marginTop: 8, color: "#5B6B7B" }}>选择与单词匹配的图片</Text>
          </View>
        )}

        {tab === "exam" && (
          <View style={cardStyle}>
            <Text style={{ fontSize: 18, fontWeight: "600" }}>A2 模拟考试</Text>
            <Text style={{ marginTop: 8, color: "#5B6B7B" }}>题量 20 · 时长 30 分钟</Text>
          </View>
        )}

        {tab === "report" && (
          <View style={cardStyle}>
            <Text style={{ fontSize: 18, fontWeight: "600" }}>学习报告</Text>
            <Text style={{ marginTop: 8 }}>学习记录：128</Text>
            <Text style={{ marginTop: 4 }}>正确率：82%</Text>
            <Text style={{ marginTop: 4 }}>考试均分：78</Text>
          </View>
        )}

        {tab === "profile" && (
          <View style={cardStyle}>
            <Text style={{ fontSize: 18, fontWeight: "600" }}>个人设置</Text>
            <Text style={{ marginTop: 8, color: "#5B6B7B" }}>邮箱、学习目标、提醒设置</Text>
            <TextInput
              style={{ marginTop: 12, backgroundColor: "#F1F5F9", padding: 10, borderRadius: 10 }}
              placeholder="Email"
              value={email}
              onChangeText={setEmail}
            />
            <TextInput
              style={{ marginTop: 8, backgroundColor: "#F1F5F9", padding: 10, borderRadius: 10 }}
              placeholder="Password"
              secureTextEntry
              value={password}
              onChangeText={setPassword}
            />
            <TouchableOpacity style={{ marginTop: 10 }} onPress={login}>
              <Text style={{ color: "#1F6BFF" }}>登录</Text>
            </TouchableOpacity>
            <Text style={{ marginTop: 8, color: "#5B6B7B" }}>{status}</Text>
            {token ? <Text style={{ marginTop: 4 }}>已获取 Token</Text> : null}
          </View>
        )}
      </ScrollView>

      <View style={{ flexDirection: "row", justifyContent: "space-around", padding: 12, backgroundColor: "#ffffff" }}>
        {tabs.map((item) => (
          <TouchableOpacity key={item.key} onPress={() => setTab(item.key)}>
            <Text style={{ color: tab === item.key ? "#1F6BFF" : "#5B6B7B" }}>{item.label}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </SafeAreaView>
  );
}
