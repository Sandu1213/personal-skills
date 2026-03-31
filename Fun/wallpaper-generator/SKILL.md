---
name: wallpaper-generator
description: 用户输入主题，自动扩展并生成6张覆盖主流机型比例（iPhone/Samsung/Huawei/Xiaomi）的手机壁纸,生成的图片保存在wallpapers文件夹下,图片命名格式为 wallpaper_[theme]_[机型].png,图片质量为4k
---

# Phone Wallpaper Generator Skill

## Goal
Generate 6 high-quality mobile wallpapers based on a user-provided theme. The wallpapers should cover different artistic styles and target vertical aspect ratios suitable for mainstream phones (iPhone, Samsung, Huawei, Xiaomi).

## Workflow

### 1. Theme Analysis & Expansion
Ask the user for the **Theme** (if not already provided).
Based on the theme, brainstorm 6 distinct visual concepts.
*   **Concept 1 (iPhone Style)**: Elegant, high-end, suitable for notched screens. (Target Ratio: 19.5:9)
*   **Concept 2 (Samsung Style)**: Vibrant colors, AMOLED optimized, deep blacks. (Target Ratio: 20:9)
*   **Concept 3 (Huawei Style)**: Scenic, grand, photographic or painterly. (Target Ratio: 19:9)
*   **Concept 4 (Xiaomi Style)**: Modern, tech-focused or minimalist. (Target Ratio: 20:9)
*   **Concept 5 (General Vertical)**: Abstract or Pattern-based. (Target Ratio: 9:16)
*   **Concept 6 (Creative/Artistic)**: A unique interpretation of the theme.

### 2. Image Generation Loop
For each concept, generate an image using the `generate_image` tool.
**Critical:** Since the tool usage is prompt-based, you MUST include keywords to enforce vertical composition and high quality.

**Prompt Structure:**
`[Expanded Theme Description], mobile phone wallpaper, vertical 9:16 aspect ratio, 8k resolution, highly detailed, aesthetic, [Specific Style Keywords]`

**Step-by-Step Execution:**

1.  **Generate Wallpaper 1**:
    *   **Prompt**: [Concept 1 Description] + "vertical wallpaper, 19.5:9 aspect ratio, fit for iPhone"
    *   **Name**: `wallpaper_[theme]_iphone`
2.  **Generate Wallpaper 2**:
    *   **Prompt**: [Concept 2 Description] + "vertical wallpaper, 20:9 aspect ratio, vibrant colors, fit for Samsung"
    *   **Name**: `wallpaper_[theme]_samsung`
3.  **Generate Wallpaper 3**:
    *   **Prompt**: [Concept 3 Description] + "vertical wallpaper, 19:9 aspect ratio, fit for Huawei"
    *   **Name**: `wallpaper_[theme]_huawei`
4.  **Generate Wallpaper 4**:
    *   **Prompt**: [Concept 4 Description] + "vertical wallpaper, 20:9 aspect ratio, fit for Xiaomi"
    *   **Name**: `wallpaper_[theme]_xiaomi`
5.  **Generate Wallpaper 5**:
    *   **Prompt**: [Concept 5 Description] + "vertical wallpaper, 9:16 aspect ratio, abstract"
    *   **Name**: `wallpaper_[theme]_abstract`
6.  **Generate Wallpaper 6**:
    *   **Prompt**: [Concept 6 Description] + "vertical wallpaper, cinematic lighting, 4k"
    *   **Name**: `wallpaper_[theme]_creative`

### 3. Final Deliverable
Present the 6 generated images to the user.
Ask which one they like best or if they need adjustments.
