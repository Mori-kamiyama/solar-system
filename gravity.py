import arcade
import arcade.gui
import numpy as np

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SCREEN_TITLE = "三体"

# トレイルの長さを保持するための定数
TRAIL_LENGTH = 100

# 円の初期プロパティを定義する関数
def create_circles():
    return [
        {"x": np.random.rand() * 200 + 400, "y": np.random.rand() * 200 + 250, "radius": np.random.rand() * 10 + 5,
         "color": (227, 55, 30),
         "v": np.random.rand(2) * 100 - 50, "trail": []},
        {"x": np.random.rand() * 200 + 400, "y": np.random.rand() * 200 + 250, "radius": np.random.rand() * 10 + 5,
         "color": (5, 147, 162),
         "v": np.random.rand(2) * 100 - 50, "trail": []},
        {"x": np.random.rand() * 200 + 400, "y": np.random.rand() * 200 + 250, "radius": np.random.rand() * 10 + 5,
         "color": (255, 122, 72),
         "v": np.random.rand(2) * 100 - 50, "trail": []},
        {"x": np.random.rand() * 200 + 400, "y": np.random.rand() * 200 + 250, "radius": np.random.rand() * 10 + 5,
         "color": (16, 55, 120),
         "v": np.random.rand(2) * 100 - 50, "trail": []},
    ]

# 円のリストを初期化
circles = create_circles()

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color((10, 20, 30))

        # カメラの初期化
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        # ボタンを管理するためのUIマネージャを作成
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # ボタンを横に並べるためのUIボックスレイアウトを作成
        self.h_box = arcade.gui.UIBoxLayout(vertical=False)

        # リスタートボタンを作成 (アイコン)
        restart_texture = arcade.load_texture("restart.png")
        restart_button = arcade.gui.UITextureButton(texture=restart_texture, width=64, height=64)
        self.h_box.add(restart_button.with_space_around(right=20))

        # 停止ボタンを作成 (アイコン)
        stop_texture = arcade.load_texture("stop.png")
        stop_button = arcade.gui.UITextureButton(texture=stop_texture, width=64, height=64)
        self.h_box.add(stop_button.with_space_around(right=20))

        # コールバック関数をボタンに割り当て
        restart_button.on_click = self.on_restart_click
        stop_button.on_click = self.on_stop_click

        # h_boxをUIマネージャに追加し、ウィンドウに配置
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="bottom",
                child=self.h_box)
        )

        # 描画関数と更新関数のスケジュールを設定
        arcade.schedule(self.on_update, 1 / 60)

    def on_draw(self):
        arcade.start_render()  # 描画を開始

        # カメラを更新
        self.camera.use()

        # 各円とそのトレイルを描画
        for circle in circles:
            # トレイルを描画（徐々に細くなる線で）
            if len(circle["trail"]) > 1:
                for i in range(len(circle["trail"]) - 1):
                    start_point = circle["trail"][i]
                    end_point = circle["trail"][i + 1]
                    # このトレイルセグメントの幅を計算
                    width = circle["radius"] / 2 * (i + 1) / len(circle["trail"])
                    arcade.draw_line(start_point[0], start_point[1], end_point[0], end_point[1], circle["color"], width)

            # 円を描画
            arcade.draw_circle_filled(circle["x"], circle["y"], circle["radius"], circle["color"])

        # UIマネージャーを描画
        self.manager.draw()

    def on_update(self, delta_time):
        # 重力を適用して位置を更新
        for circle in circles:
            a = acceleration(circle)
            circle["v"] += a * delta_time
            circle["x"] += circle["v"][0] * delta_time
            circle["y"] += circle["v"][1] * delta_time

            # トレイルを更新
            circle["trail"].append((circle["x"], circle["y"]))

            # トレイルの長さを制限
            if len(circle["trail"]) > TRAIL_LENGTH:
                circle["trail"].pop(0)

        # カメラを中心に追従させる
        self.center_camera_to_all_circles()

    def center_camera_to_all_circles(self):
        # 全ての円の位置の平均を計算
        avg_x = np.mean([circle["x"] for circle in circles])
        avg_y = np.mean([circle["y"] for circle in circles])

        # カメラを中心に設定
        self.camera.move_to((avg_x - SCREEN_WIDTH / 2, avg_y - SCREEN_HEIGHT / 2))

    def on_restart_click(self, event):
        global circles
        circles = create_circles()  # 円を初期状態にリセット

    def on_stop_click(self, event):
        arcade.exit()  # プログラムを終了

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.on_stop_click(None)  # エスケープキーが押されたら停止

def acceleration(current_circle):
    G = 9.8  # 任意の重力定数
    a = np.array([0.0, 0.0], dtype=np.float64)  # 加速度を初期化

    for other_circle in circles:
        if other_circle == current_circle:
            continue  # 自分自身をスキップ

        # 距離ベクトルを計算
        distance_vector = np.array([other_circle["x"] - current_circle["x"],
                                    other_circle["y"] - current_circle["y"]])
        distance = np.linalg.norm(distance_vector)

        if distance > 0:  # 零距離を避ける
            # 距離に反比例して加速度を計算
            a += distance_vector * (G * current_circle["radius"] * other_circle["radius"] / (distance ** 2))

    return a

def main():
    game = MyGame()
    arcade.run()

if __name__ == "__main__":
    main()