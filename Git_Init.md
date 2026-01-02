# Lộ Trình Thực Hành Git - Từ Cơ Bản Đến Chuyên Gia

## **LEVEL 1: Cơ Bản (Tuần 1-2)**

### Bài 1: Khởi tạo và Commits cơ bản
```bash
# Tạo project mới
mkdir my-embedded-project
cd my-embedded-project
git init

# Thực hành:
- Tạo file main.c, config.h
- Thực hiện 5 commits với các thay đổi khác nhau
- Xem lịch sử: git log --oneline --graph
- Sửa commit message cuối: git commit --amend
```

Đúng rồi! **TẤT CẢ** dữ liệu Git của project nằm trong thư mục `.git` đó.

---

## **Cơ Chế Hoạt Động**

```
D:/Projects/MikroTik/
├── .git/                    ← TẤT CẢ dữ liệu Git ở đây
│   ├── objects/             ← Tất cả commits, files, history
│   ├── refs/                ← Branches, tags
│   ├── HEAD                 ← Branch hiện tại
│   ├── config               ← Cấu hình local
│   ├── hooks/               ← Git hooks
│   └── logs/                ← Lịch sử thay đổi
│
├── src/                     ← Working directory (code của bạn)
├── main.c
└── README.md
```

---

## **Chứng Minh**

```bash
# Xem dung lượng thư mục .git
du -sh .git/
# Ví dụ: 150MB (chứa toàn bộ lịch sử 2 năm)

# Xóa thư mục .git
rm -rf .git/

# Giờ check git status
git status
# fatal: not a git repository

# MẤT HẾT:
# ❌ Tất cả commits
# ❌ Tất cả branches
# ❌ Toàn bộ lịch sử
# ✅ Code vẫn còn (working directory)
```

---

## **Chi Tiết Bên Trong `.git/`**

### **1. `.git/objects/` - Kho Lưu Trữ**
Chứa TẤT CẢ:
- Mọi commit bạn từng tạo
- Mọi file trong mọi version
- Mọi tree (cấu trúc thư mục)

```bash
# Xem objects
ls .git/objects/
# 00/ 01/ 02/ ... ff/  (256 thư mục)

# Mỗi file là 1 object (commit, blob, tree)
```

**Ví dụ:** Bạn commit file `gps.c` 10 lần → có 10 versions của `gps.c` lưu trong `objects/`

### **2. `.git/refs/` - Branches và Tags**
```bash
.git/refs/
├── heads/          ← Local branches
│   ├── main
│   ├── develop
│   └── feature/gps
├── remotes/        ← Remote branches
│   └── origin/
│       ├── main
│       └── develop
└── tags/           ← Tags (v1.0, v2.0)
```

### **3. `.git/HEAD` - Branch Hiện Tại**
```bash
cat .git/HEAD
# ref: refs/heads/main

# Khi switch branch:
git checkout develop
cat .git/HEAD
# ref: refs/heads/develop
```

### **4. `.git/config` - Cấu Hình Local**
```ini
[core]
    repositoryformatversion = 0
[remote "origin"]
    url = https://github.com/user/mikrotik.git
    fetch = +refs/heads/*:refs/remotes/origin/*
[branch "main"]
    remote = origin
    merge = refs/heads/main
```

---

## **Use Cases Thực Tế**

### **Case 1: Backup Project**
```bash
# Backup CẢ project + lịch sử Git
cp -r D:/Projects/MikroTik D:/Backup/MikroTik

# Hoặc chỉ backup code (không lịch sử)
cp -r D:/Projects/MikroTik D:/Backup/MikroTik-code-only
rm -rf D:/Backup/MikroTik-code-only/.git
```

### **Case 2: Chuyển Project Sang Máy Khác**
```bash
# Cách 1: Copy cả thư mục (bao gồm .git)
# → Có đầy đủ lịch sử, branches

# Cách 2: Clone từ remote
git clone https://github.com/user/mikrotik.git
# → Giống hệt, đầy đủ lịch sử
```

### **Case 3: "Xóa" Lịch Sử Git**
```bash
# Scenario: Muốn bắt đầu Git mới, xóa lịch sử cũ
rm -rf .git/
git init
git add .
git commit -m "Initial commit"

# Giờ chỉ có 1 commit, mất hết lịch sử cũ
```

**Khi nào dùng:**
- ✅ Commit nhầm passwords vào lịch sử → xóa .git, init lại
- ✅ Project cũ rối, muốn bắt đầu lại
- ❌ KHÔNG làm nếu team đang làm việc chung!

### **Case 4: Git Repository Bị Hỏng**
```bash
# Lỗi: .git/objects bị corrupt
git status
# error: object file .git/objects/xx/xxx is empty

# Giải pháp 1: Clone lại từ remote
cd ..
rm -rf MikroTik
git clone https://github.com/user/mikrotik.git

# Giải pháp 2: Sửa (nếu không có remote)
git fsck --full
# Tìm và fix corrupted objects
```

### **Case 5: Dung Lượng `.git/` Quá Lớn**
```bash
# Scenario: .git/ lên tới 2GB vì commit nhầm file lớn

# Xem file lớn
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  sed -n 's/^blob //p' | \
  sort --numeric-sort --key=2 | \
  tail -n 10

# Xóa file khỏi lịch sử (nguy hiểm!)
git filter-branch --tree-filter 'rm -f big_file.bin' HEAD

# Dọn dẹp
git gc --aggressive --prune=now

# Kết quả: .git/ giảm từ 2GB xuống 50MB
```

---

## **So Sánh: Local Project vs Git Repository**

| | Không có Git | Có Git |
|---|---|---|
| **Thư mục** | `D:/Projects/MikroTik/` | `D:/Projects/MikroTik/` |
| **Code** | `src/`, `main.c`, ... | `src/`, `main.c`, ... (giống hệt) |
| **Lịch sử** | ❌ Không có | ✅ Trong `.git/objects/` |
| **Branches** | ❌ Không có | ✅ Trong `.git/refs/` |
| **Backup** | Phải copy thủ công | `git push` lên remote |
| **Rollback** | ❌ Không thể | `git reset`, `git revert` |

---

## **Kiểm Tra Thực Tế**

```bash
# 1. Xem kích thước .git
du -sh .git/
# Ví dụ: 120MB

# 2. Xem số objects (commits, files, trees)
git count-objects -v
# count: 1523
# size: 125000 KB

# 3. Xem tất cả branches (local + remote)
git branch -a
# * main
#   develop
#   feature/gps
#   remotes/origin/main
#   remotes/origin/develop

# 4. Xem cấu hình
cat .git/config
```

---

## **Kết Luận**

✅ **ĐÚNG:** Tất cả dữ liệu Git nằm trong `.git/`

**Điều này có nghĩa:**
1. Xóa `.git/` = mất hết lịch sử, branches, commits
2. Copy project = copy cả `.git/` → có đầy đủ lịch sử
3. `.git/` có thể rất lớn nếu nhiều commits hoặc commit file lớn
4. Working directory (code của bạn) độc lập với `.git/`

**Tương tự:**
- `.git/` giống như database lưu lịch sử
- Working directory là nơi bạn làm việc
- `git checkout` = lấy version từ database ra working directory

Bạn có muốn tôi giải thích sâu hơn về cấu trúc bên trong `.git/objects/` (cách Git lưu trữ commits và files) không?

---

Bạn đúng! Tôi bổ sung chi tiết về **Git Commit** và **Xử lý lỗi thường gặp**.

---

## **FIX LỖI CỦA BẠN NGAY**

```bash
# Lỗi: Git không tin tưởng thư mục này (thường trên Windows)
# Fix:
git config --global --add safe.directory D:/Projects/MikroTik

# Sau đó commit lại:
git commit -m "add init files"
```

**Tại sao có lỗi này?**
- Windows file system không lưu ownership như Linux
- Git nghĩ có nguy cơ bảo mật → từ chối
- Fix: Báo Git "tin tưởng" thư mục này

---

# **Chi Tiết: Git Commit - Từ A đến Z**

## **1. Workflow Cơ Bản**

```bash
# Bước 1: Kiểm tra status
git status

# Bước 2: Add files vào staging area
git add <files>

# Bước 3: Commit
git commit -m "message"

# Bước 4: Push lên remote (nếu có)
git push
```

---

## **2. Git Add - Thêm Files Vào Staging**

### **Các Cách Add**

```bash
# Add 1 file cụ thể
git add main.c

# Add nhiều files
git add main.c gps.c config.h

# Add tất cả files trong thư mục
git add src/

# Add TẤT CẢ files đã thay đổi (tracked files)
git add -u

# Add TẤT CẢ (bao gồm untracked files)
git add .
git add -A
git add --all

# Add interactive (chọn từng thay đổi)
git add -p
# Git hỏi từng hunk: Stage this hunk [y,n,q,a,d,e,?]?
```

### **So Sánh `git add` Options**

| Command | Tracked Files | Untracked Files | Deleted Files |
|---------|--------------|-----------------|---------------|
| `git add .` | ✅ Add | ✅ Add | ✅ Add |
| `git add -A` | ✅ Add | ✅ Add | ✅ Add |
| `git add -u` | ✅ Add | ❌ Không add | ✅ Add |
| `git add <file>` | ✅ Add | ✅ Add | ❌ |

**Use Case:**
```bash
# Scenario: Có 5 files mới, 3 files sửa, 2 files xóa

git add -A        # Add TẤT CẢ (10 files)
git add -u        # Add 3 sửa + 2 xóa (bỏ qua 5 files mới)
git add src/      # Add tất cả trong src/ folder
```

---

## **3. Git Commit - Các Tham Số Chi Tiết**

### **Commit Cơ Bản**

```bash
# Commit với message ngắn
git commit -m "feat: add GPS module"

# Commit với message dài (mở editor)
git commit
# Editor mở, gõ message nhiều dòng

# Commit TẤT CẢ tracked files (bỏ qua git add)
git commit -a -m "fix: resolve UART timeout"
# = git add -u + git commit -m

# Commit và add (CHỈ tracked files)
git commit -am "update GPS parsing"
```

### **Commit Message Multi-line**

```bash
# Cách 1: Dùng editor
git commit
# Editor mở:
# feat: add GPS coordinate parsing
#
# - Support NMEA format
# - Add validation for lat/lon
# - Handle edge cases

# Cách 2: Command line (Windows)
git commit -m "feat: add GPS parsing" -m "Support NMEA format" -m "Add validation"

# Cách 3: Heredoc (Linux/Mac)
git commit -m "$(cat <<EOF
feat: add GPS parsing

- Support NMEA format  
- Add validation
- Handle edge cases
EOF
)"
```

### **Commit Advanced Options**

```bash
# Sửa commit cuối cùng (chưa push)
git commit --amend -m "fix: correct GPS timeout to 1000ms"

# Thêm file vào commit cuối (quên add)
git add forgotten_file.c
git commit --amend --no-edit
# --no-edit: giữ nguyên commit message

# Commit với author khác
git commit -m "feat: GPS" --author="John Doe <john@example.com>"

# Commit với date cụ thể
git commit -m "feat: GPS" --date="2024-01-15 10:00:00"

# Commit empty (không có thay đổi)
git commit --allow-empty -m "trigger CI/CD"

# Commit với GPG signature
git commit -S -m "feat: secure commit"
```

### **Commit Message Best Practices**

```bash
# ❌ BAD
git commit -m "update"
git commit -m "fix bug"
git commit -m "asdf"
git commit -m "changes"

# ✅ GOOD
git commit -m "feat: add GPS coordinate parsing function"
git commit -m "fix: resolve UART timeout after 30 seconds"
git commit -m "docs: update README with setup instructions"
git commit -m "refactor: simplify GPS data validation logic"
git commit -m "test: add unit tests for GPS parsing"
```

**Format chuẩn (Conventional Commits):**
```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: Tính năng mới
- `fix`: Sửa bug
- `docs`: Documentation
- `style`: Format code (không thay đổi logic)
- `refactor`: Refactor code
- `test`: Thêm tests
- `chore`: Maintenance (update dependencies, ...)

**Ví dụ đầy đủ:**
```bash
git commit -m "feat: implement GPS coordinate parsing

- Add support for NMEA 0183 format
- Validate latitude/longitude ranges
- Handle UTC timestamp conversion

Closes #123"
```

---

## **4. Xem Commits**

```bash
# Xem lịch sử commits
git log

# Xem compact (1 dòng/commit)
git log --oneline

# Xem graph (branches)
git log --oneline --graph --all

# Xem với diff
git log -p

# Xem 5 commits gần nhất
git log -5

# Xem commits theo author
git log --author="Tuan"

# Xem commits theo date
git log --since="2024-01-01"
git log --until="2024-12-31"

# Xem commits có chứa text
git log -S "gps_parse"

# Xem commits của 1 file
git log -- gps.c

# Xem commit cụ thể
git show abc1234
```

---

## **5. Staging Area - Hiểu Rõ Cơ Chế**

```
Working Directory → Staging Area → Repository
     (code)            (index)       (.git)

                git add →
                        ← git restore
                                git commit →
```

**Ví dụ:**
```bash
# Bước 1: Sửa file
echo "GPS v1" > gps.c
git status
# Changes not staged for commit:
#   modified:   gps.c

# Bước 2: Add vào staging
git add gps.c
git status
# Changes to be committed:
#   modified:   gps.c

# Bước 3: Sửa tiếp file (sau khi add)
echo "GPS v2" >> gps.c
git status
# Changes to be committed:
#   modified:   gps.c      ← Version v1 (staged)
# Changes not staged for commit:
#   modified:   gps.c      ← Version v2 (working)

# Commit chỉ lấy version v1 (staged)
git commit -m "update GPS"
# gps.c trong commit = "GPS v1"
# gps.c trong working dir = "GPS v1\nGPS v2"
```

---

## **6. Undo Staging**

```bash
# Unstage file (bỏ ra khỏi staging)
git restore --staged gps.c
# Hoặc (cách cũ):
git reset HEAD gps.c

# Unstage tất cả
git restore --staged .
git reset HEAD .

# Discard working changes (nguy hiểm!)
git restore gps.c
# Hoặc:
git checkout -- gps.c
```

---

## **7. LỖI THƯỜNG GẶP & CÁCH FIX**

### **Lỗi 1: Dubious Ownership (của bạn)**
```bash
fatal: detected dubious ownership in repository at 'D:/Projects/MikroTik'

# Fix:
git config --global --add safe.directory D:/Projects/MikroTik

# Hoặc trust tất cả (không khuyến khích):
git config --global --add safe.directory '*'
```

### **Lỗi 2: Nothing to Commit**
```bash
git commit -m "update"
# On branch main
# nothing to commit, working tree clean

# Nguyên nhân: Quên git add
# Fix:
git add .
git commit -m "update"
```

### **Lỗi 3: Please Tell Me Who You Are**
```bash
git commit -m "test"
# fatal: unable to auto-detect email address

# Fix: Config user
git config --global user.name "Tuan Nguyen"
git config --global user.email "tuan@example.com"

# Hoặc chỉ cho repo này:
git config user.name "Tuan"
git config user.email "tuan@example.com"
```

### **Lỗi 4: LF Will Be Replaced by CRLF**
```bash
warning: LF will be replaced by CRLF in main.c

# Giải thích: Windows dùng CRLF, Linux dùng LF
# Fix (Windows):
git config --global core.autocrlf true

# Fix (Linux/Mac):
git config --global core.autocrlf input
```

### **Lỗi 5: Cannot Commit (Files in .gitignore)**
```bash
# Thêm file vào .gitignore rồi mới add
git add build/output.hex
# The following paths are ignored by one of your .gitignore files

# Fix: Force add
git add -f build/output.hex

# Hoặc: Bỏ khỏi .gitignore
```

### **Lỗi 6: Commit Sai Branch**
```bash
# Đang ở main, commit nhầm
git add .
git commit -m "new feature"
# Ối, phải commit vào feature branch!

# Fix: Chuyển commit sang branch khác
git branch feature/my-work    # Tạo branch tại commit này
git reset --hard HEAD~1       # Xóa commit ở main
git checkout feature/my-work  # Switch sang branch mới
```

### **Lỗi 7: Commit Message Sai**
```bash
git commit -m "updat"  # Typo!

# Fix: Sửa commit cuối
git commit --amend -m "update GPS parsing"
```

### **Lỗi 8: Quên Add File Vào Commit**
```bash
git commit -m "add GPS module"
# Quên add gps.h!

# Fix:
git add gps.h
git commit --amend --no-edit
# Thêm gps.h vào commit cuối
```

### **Lỗi 9: File Quá Lớn**
```bash
git add firmware.bin  # 500MB
git commit -m "add firmware"
# warning: adding embedded git repository

# Fix: Dùng Git LFS
git lfs install
git lfs track "*.bin"
git add .gitattributes
git add firmware.bin
git commit -m "add firmware with LFS"
```

### **Lỗi 10: Permission Denied (SSH)**
```bash
git push origin main
# Permission denied (publickey)

# Fix: Setup SSH key
ssh-keygen -t ed25519 -C "tuan@example.com"
cat ~/.ssh/id_ed25519.pub
# Copy key, paste vào GitHub Settings → SSH Keys
```

---

## **8. Workflow Thực Tế - Bước Từng Bước**

### **Scenario: Code Feature Mới**

```bash
# Bước 1: Kiểm tra status
git status
# On branch main
# Your branch is up to date with 'origin/main'

# Bước 2: Tạo branch mới
git checkout -b feature/gps-module

# Bước 3: Code...
vim src/gps.c
vim src/gps.h

# Bước 4: Kiểm tra thay đổi
git status
# Untracked files:
#   src/gps.c
#   src/gps.h

git diff  # Không có gì (files chưa tracked)

# Bước 5: Add files
git add src/gps.c src/gps.h

# Bước 6: Kiểm tra lại
git status
# Changes to be committed:
#   new file:   src/gps.c
#   new file:   src/gps.h

git diff --staged  # Xem thay đổi sẽ commit

# Bước 7: Commit
git commit -m "feat: add GPS coordinate parsing module

- Implement NMEA parser
- Add latitude/longitude validation
- Support GGA and RMC sentences"

# Bước 8: Xem lịch sử
git log --oneline -1
# abc1234 feat: add GPS coordinate parsing module

# Bước 9: Push lên remote
git push -u origin feature/gps-module
```

### **Scenario: Fix Bug Gấp**

```bash
# Đang code feature, có bug production

# Bước 1: Stash công việc hiện tại
git stash save "WIP: GPS module"

# Bước 2: Về main branch
git checkout main

# Bước 3: Tạo hotfix branch
git checkout -b hotfix/uart-timeout

# Bước 4: Fix bug
vim src/uart.c

# Bước 5: Test...

# Bước 6: Commit
git add src/uart.c
git commit -m "fix: increase UART timeout to 1000ms

Resolves timeout issues when GPS module responds slowly"

# Bước 7: Merge vào main
git checkout main
git merge hotfix/uart-timeout

# Bước 8: Push
git push origin main

# Bước 9: Quay lại công việc cũ
git checkout feature/gps-module
git stash pop
```

---

## **9. Git Commit Checklist**

Trước KHI commit, check:

```bash
# ✅ 1. Code chạy được?
# Test code trước

# ✅ 2. Có debug code không?
git diff | grep -i "printf\|console.log\|debugger"

# ✅ 3. Có TODO không?
git diff | grep -i "TODO\|FIXME"

# ✅ 4. Commit message rõ ràng?
# Không: "update", "fix", "asdf"
# Có: "feat: add GPS parsing"

# ✅ 5. Commit đúng files?
git status  # Check lại

# ✅ 6. Code style OK?
# Chạy linter nếu có

# ✅ 7. Có file sensitive không?
git diff | grep -i "password\|secret\|api.key"
```

---

Bạn muốn tôi chi tiết hóa thêm phần nào? Ví dụ:
- Git config chi tiết?
- Các lệnh git log nâng cao?
- Setup Git cho embedded project cụ thể (STM32)?

---


### Bài 2: .gitignore và Git Status
```bash
# Tạo file .gitignore cho embedded project
*.o
*.hex
*.elf
build/
.vscode/

# Thực hành:
- Tạo các file nên ignore và không nên ignore
- Kiểm tra git status
- Thử git add -A vs git add .
```

### Bài 3: Xem thay đổi
```bash
# Thực hành:
- git diff (unstaged changes)
- git diff --staged (staged changes)
- git diff HEAD~1 (so với commit trước)
- git show <commit-hash>
```

---

## **LEVEL 2: Trung Bình (Tuần 3-4)**

### Bài 4: Branching Strategy
```bash
# Tạo workflow thực tế
git branch develop
git checkout -b feature/gps-module
git checkout -b feature/web-interface

# Thực hành:
- Làm việc trên 3 branch song song
- Tạo ít nhất 3 commits trên mỗi branch
- Xem git log --all --graph --decorate
```

### Bài 5: Merging và Conflicts
```bash
# Tạo conflicts cố ý
- Sửa cùng 1 dòng code ở 2 branch khác nhau
- Merge và giải quyết conflict
- Thử cả merge --no-ff và merge --squash
- So sánh git log sau mỗi kiểu merge

# Advanced:
- Thử merge strategy: -X ours, -X theirs
```

### Bài 6: Remote Repository
```bash
# Setup remote (GitHub/GitLab)
git remote add origin <url>
git push -u origin main

# Thực hành:
- Clone repo về máy khác
- Tạo conflicts giữa local và remote
- git fetch vs git pull
- Đẩy nhiều branch lên remote
```

---

## **LEVEL 3: Nâng Cao (Tuần 5-7)**

### Bài 7: Rebase Mastery
```bash
# Interactive rebase
git rebase -i HEAD~5

# Thực hành:
- Squash nhiều commits thành 1
- Reorder commits
- Edit commit messages
- Drop commits không cần thiết
- Tách 1 commit thành nhiều commits

# Rebase branch
git rebase main feature/gps-module
```

### Bài 8: Stash và WIP Management
```bash
# Scenarios:
- Đang code dở, cần switch branch gấp
- git stash save "WIP: GPS interrupt handler"
- git stash list
- git stash pop vs git stash apply
- git stash branch new-feature stash@{0}
- git stash drop

# Advanced:
- git stash -p (partial stash)
- git stash show -p stash@{0}
```

### Bài 9: Reset, Revert và Undo
```bash
# Thực hành các scenario:
1. Undo commit cuối (giữ changes): git reset --soft HEAD~1
2. Undo commit cuối (mất changes): git reset --hard HEAD~1
3. Undo commit ở giữa: git revert <hash>
4. Undo staged files: git reset HEAD file.c
5. Undo working changes: git checkout -- file.c

# Dangerous zone:
- git reset --hard origin/main (đồng bộ với remote)
- git clean -fd (xóa untracked files)
```

### Bài 10: Cherry-pick
```bash
# Scenario: Lấy 1 commit cụ thể từ branch khác
git cherry-pick <commit-hash>
git cherry-pick <hash1> <hash2> <hash3>

# Thực hành:
- Copy bugfix từ develop sang hotfix branch
- Giải quyết cherry-pick conflicts
```

---

## **LEVEL 4: Chuyên Gia (Tuần 8-10)**

### Bài 11: Git Reflog - Time Machine
```bash
# Recovery scenarios:
- git reset --hard nhầm
- git reflog
- git reset --hard HEAD@{2}

# Thực hành:
- "Xóa" branch rồi recover lại
- Tìm commit đã mất
- Restore deleted commits
```

### Bài 12: Git Bisect - Bug Hunting
```bash
# Tìm commit gây bug
git bisect start
git bisect bad HEAD
git bisect good v1.0
# Git sẽ checkout từng commit để test

# Thực hành:
- Tạo 20 commits, 1 commit có bug
- Dùng bisect để tìm commit lỗi
- Tự động hóa: git bisect run ./test-script.sh
```

### Bài 13: Git Hooks
```bash
# Tạo hooks cho workflow
cd .git/hooks

# pre-commit: Check code style
cat > pre-commit << 'EOF'
#!/bin/bash
if grep -r "TODO" *.c; then
    echo "Found TODO in code!"
    exit 1
fi
EOF
chmod +x pre-commit

# Thực hành:
- pre-commit: kiểm tra trailing whitespace
- commit-msg: format commit message
- post-merge: cảnh báo conflicts
- pre-push: chạy tests
```

### Bài 14: Submodules
```bash
# Quản lý dependencies
git submodule add <repo-url> libs/esp32-lib
git submodule init
git submodule update

# Thực hành:
- Thêm 2-3 submodules
- Update submodule lên version mới
- Clone repo có submodules
- git clone --recursive
```

### Bài 15: Advanced Workflows
```bash
# Git Flow
git flow init
git flow feature start new-sensor
git flow feature finish new-sensor

# Worktree (làm việc nhiều branch cùng lúc)
git worktree add ../project-hotfix hotfix
cd ../project-hotfix
# Code ở branch hotfix không ảnh hưởng main

# Thực hành:
- Setup Git Flow cho project
- Dùng worktree cho hotfix
- Release workflow hoàn chỉnh
```

---

## **LEVEL 5: Master (Tuần 11-12)**

### Bài 16: Git Internals
```bash
# Hiểu cách Git hoạt động
git cat-file -p HEAD
git ls-tree HEAD
git rev-parse HEAD

# Thực hành:
- Xem objects trong .git/objects
- Hiểu blob, tree, commit objects
- Tìm hiểu Git packfiles
```

### Bài 17: Performance Optimization
```bash
# Large repositories
git gc --aggressive
git prune
git fsck

# Shallow clone
git clone --depth=1 <url>

# Sparse checkout (chỉ checkout 1 phần)
git sparse-checkout init
git sparse-checkout set src/
```

### Bài 18: Advanced Search & Filter
```bash
# Tìm kiếm trong lịch sử
git log -S "function_name" # Tìm commits thêm/xóa text
git log -G "regex_pattern" # Tìm theo regex
git log -- path/to/file # Lịch sử 1 file
git blame file.c # Ai sửa dòng nào

# Filter branch
git filter-branch --tree-filter 'rm -f password.txt' HEAD
# Hoặc dùng git-filter-repo (modern)
```

---

## **🎯 Project Cuối Khóa: Embedded System Project**

Áp dụng tất cả kiến thức vào 1 project thực tế:

```
Yêu cầu:
✓ Setup Git Flow workflow
✓ Minimum 3 developers (tự mô phỏng)
✓ Feature branches: GPS, WebUI, Logging
✓ Use submodules cho libraries
✓ Setup pre-commit hooks
✓ Create release tags
✓ Handle hotfix scenario
✓ Document trong README.md với badges
✓ CI/CD integration (GitHub Actions)
```

---

## **📚 Tài Nguyên Thêm**

1. **Thực hành mỗi ngày**: Commit code công việc với message chuẩn
2. **Đọc Git documentation**: `git help <command>`
3. **Visualize**: Dùng GitKraken hoặc SourceTree để thấy graph
4. **Oh Shit, Git!**: https://ohshitgit.com/ (khi gặp vấn đề)

Bạn muốn tôi chi tiết hóa bài tập nào, hoặc tạo script tự động để practice không?


# Lộ Trình Thực Hành Git - Từ Cơ Bản Đến Chuyên Gia
## (Có Use Cases Thực Tế)

---

## **LEVEL 1: Cơ Bản (Tuần 1-2)**

### Bài 1: Commits Đúng Cách
```bash
git commit -m "feat: add GPS coordinate parsing function"
git commit -m "fix: resolve UART interrupt race condition"
git commit -m "docs: update README with NTP server setup"
```

**Use Cases:**
1. **Code review dễ dàng**: Teammate đọc lịch sử hiểu ngay bạn làm gì
2. **Rollback chính xác**: Khi GPS module có bug, bạn biết commit nào cần revert
3. **Release notes tự động**: Tool có thể generate changelog từ commit messages
4. **Debugging**: `git bisect` dễ dàng hơn khi commit message rõ ràng

**Khi nào dùng:**
- ✅ Mỗi tính năng hoàn chỉnh = 1 commit (GPS parsing xong → commit)
- ✅ Mỗi bugfix = 1 commit riêng
- ❌ KHÔNG commit code chưa chạy được
- ❌ KHÔNG commit với message "update", "fix bug", "asdfgh"

**Thực hành:**
```bash
# Scenario: Bạn code GPS module
1. Viết hàm parse_gps_coordinates() → commit "feat: add GPS parsing"
2. Fix bug UART timeout → commit "fix: increase UART timeout to 1000ms"
3. Thêm unit test → commit "test: add GPS parsing test cases"
```

---

### Bài 2: .gitignore - Giữ Repo Sạch

**Use Cases:**

**Case 1: Build Artifacts**
```bash
# Scenario: Bạn build firmware
*.o          # Object files từ compiler
*.elf        # Binary output
*.hex        # Flash file
build/       # Thư mục build
```
**Tại sao?** Build files khác nhau trên mỗi máy, commit chúng làm repo phình to, conflicts liên tục.

**Case 2: IDE Settings**
```bash
.vscode/     # VS Code settings
.idea/       # IntelliJ
*.swp        # Vim swap files
```
**Tại sao?** Mỗi dev có config riêng, không nên ép người khác dùng settings của bạn.

**Case 3: Sensitive Data**
```bash
config/secrets.h    # API keys, passwords
*.pem               # Private keys
.env                # Environment variables
```
**Tại sao?** BẢO MẬT! Đẩy password lên GitHub = tai họa.

**Case 4: Log Files**
```bash
logs/
*.log
debug_output.txt
```
**Tại sao?** Log files thay đổi liên tục, gây noise trong git status.

**Khi nào KHÔNG ignore:**
- ✅ Shared configs: `.vscode/extensions.json` (recommend extensions cho team)
- ✅ Example files: `config.example.h` (template cho secrets)

**Thực hành:**
```bash
# Scenario: Embedded project
echo "*.o" >> .gitignore
echo "*.elf" >> .gitignore
echo "build/" >> .gitignore
echo "config/secrets.h" >> .gitignore

# Nhưng commit:
git add config/secrets.example.h  # Template file
```

---

### Bài 3: Git Diff - Xem Trước Khi Commit

**Use Cases:**

**Case 1: Review Code Trước Khi Commit**
```bash
git diff
```
**Scenario:** Bạn vừa sửa 10 files trong 2 tiếng. Trước khi commit, cần check:
- ❓ Có debug code `printf()` nào quên xóa không?
- ❓ Có comment code out nào không cần thiết?
- ❓ Có thay đổi nào không liên quan (ví dụ format lại toàn file)?

**Case 2: So Sánh Với Commit Trước**
```bash
git diff HEAD~1
```
**Scenario:** Sau khi merge pull request, firmware không chạy. Cần xem "thay đổi gì so với version cũ?"

**Case 3: So Sánh Giữa Các Branch**
```bash
git diff develop feature/gps-module
```
**Scenario:** Trước khi merge feature branch vào develop, xem tổng quan thay đổi gì.

**Case 4: Xem Thay Đổi Của 1 File Cụ Thể**
```bash
git diff HEAD~1 src/gps.c
```
**Scenario:** GPS module có bug, muốn xem file `gps.c` thay đổi gì so với commit trước.

**Khi nào dùng:**
- ✅ Trước MỌI commit → tránh commit nhầm
- ✅ Khi code review → hiểu teammate làm gì
- ✅ Debugging → tìm xem thay đổi nào gây lỗi

**Thực hành:**
```bash
# Sửa file main.c
# Thêm debug code printf()
git diff                    # Thấy debug code → xóa trước khi commit
git add main.c
git diff --staged          # Review lần cuối
git commit
```

---

## **LEVEL 2: Trung Bình (Tuần 3-4)**

### Bài 4: Branching - Làm Việc Song Song

**Use Cases:**

**Case 1: Feature Development**
```bash
git checkout -b feature/web-interface
```
**Scenario:** Bạn đang code GPS module (90% xong), sếp bảo làm thêm web interface gấp. Không muốn GPS code dở dang ảnh hưởng web interface.

**Giải pháp:** Tạo branch mới từ `main` (stable code), code web interface riêng.

**Case 2: Hotfix**
```bash
git checkout -b hotfix/uart-buffer-overflow
```
**Scenario:** Firmware đang chạy production bị crash. Cần fix GẤP mà không muốn lấy code đang dev (chưa test kỹ).

**Giải pháp:** Branch từ `main` (production code), fix bug, merge vào `main` và `develop`.

**Case 3: Experiment**
```bash
git checkout -b experiment/new-gps-library
```
**Scenario:** Muốn thử GPS library mới, nhưng không chắc có tốt hơn. Nếu không tốt → xóa branch, không ảnh hưởng code chính.

**Case 4: Multiple Versions**
```bash
git checkout -b release/v1.0
git checkout -b release/v2.0
```
**Scenario:** Khách hàng A dùng firmware v1.0, khách hàng B dùng v2.0. Khi khách hàng A báo bug → switch sang branch v1.0, fix và release.

**Khi nào dùng:**
- ✅ Mỗi feature mới = 1 branch
- ✅ Mỗi bug fix = 1 branch (nếu lớn)
- ✅ Thử nghiệm = 1 branch
- ❌ KHÔNG làm trực tiếp trên `main` branch

**Thực hành:**
```bash
# Scenario thực tế
git checkout main
git checkout -b feature/gps-module
# Code 3 ngày, 15 commits

# Sếp yêu cầu hotfix
git checkout main                    # Về code stable
git checkout -b hotfix/ntp-sync
# Fix bug, test, commit
git checkout main
git merge hotfix/ntp-sync           # Merge hotfix vào main

# Tiếp tục GPS
git checkout feature/gps-module     # Code tiếp
```

---

### Bài 5: Merge Conflicts - Giải Quyết Xung Đột

**Use Cases:**

**Case 1: 2 Dev Sửa Cùng File**
```c
// Developer A thêm:
void init_gps() {
    uart_init(9600);  // A nghĩ 9600 baud
}

// Developer B thêm:
void init_gps() {
    uart_init(115200);  // B nghĩ 115200 baud
}
```

**Khi merge:**
```bash
git merge feature/dev-b
# CONFLICT (content): Merge conflict in gps.c
```

**Giải quyết:**
```c
<<<<<<< HEAD
    uart_init(9600);
=======
    uart_init(115200);
>>>>>>> feature/dev-b
```

**Bạn phải quyết định:** Lấy 9600, 115200, hay thêm config option?

```c
// Giải pháp tốt: Make it configurable
void init_gps(uint32_t baudrate) {
    uart_init(baudrate);
}
```

**Case 2: Refactoring vs Bug Fix**
```bash
# Developer A: Refactor toàn bộ cấu trúc GPS module
# Developer B: Fix bug trong GPS module

# Khi merge → NHIỀU conflicts
```

**Giải pháp:**
1. Communicate! Báo team "đang refactor GPS module"
2. Merge `main` vào feature branch thường xuyên → conflicts nhỏ dần
3. Rebase thay vì merge (nếu branch chưa push)

**Case 3: Merge Strategy**

```bash
# Fast-forward merge (clean history)
git merge feature/small-fix

# No fast-forward (giữ branch history)
git merge --no-ff feature/gps-module
```

**Khi nào dùng `--no-ff`:**
- ✅ Feature lớn → muốn nhìn thấy branch trong history
- ✅ Cần revert cả feature → dễ dàng revert 1 merge commit
- ❌ Fix typo nhỏ → không cần

**Thực hành:**
```bash
# Tạo conflict cố ý
git checkout main
echo "GPS v1" > gps.c
git add gps.c
git commit -m "GPS v1"

git checkout -b feature/gps-v2
echo "GPS v2" > gps.c
git add gps.c
git commit -m "GPS v2"

git checkout main
echo "GPS v1.1" > gps.c
git add gps.c
git commit -m "GPS v1.1"

git merge feature/gps-v2
# CONFLICT! Giải quyết thủ công
```

---

### Bài 6: Remote Repository - Làm Việc Nhóm

**Use Cases:**

**Case 1: Backup Code**
```bash
git push origin main
```
**Scenario:** Laptop bị hỏng, mất hết code. May mà đã push lên GitHub → pull về là xong.

**Case 2: Collaborate**
```bash
git push origin feature/web-interface
```
**Scenario:** Bạn code web interface, muốn teammate review trước khi merge.

**Case 3: Sync Với Team**
```bash
git fetch origin
git pull origin develop
```

**`git fetch` vs `git pull`:**
- **`git fetch`**: Download code về nhưng KHÔNG merge vào branch hiện tại
  - **Khi nào dùng:** Muốn xem team làm gì mà không ảnh hưởng code đang làm
  ```bash
  git fetch origin
  git log origin/main  # Xem commits mới
  git diff origin/main # Xem thay đổi
  # Quyết định merge hay không
  ```

- **`git pull`**: Download VÀ merge luôn
  - **Khi nào dùng:** Chắc chắn muốn lấy code mới nhất
  ```bash
  git pull origin develop
  # = git fetch + git merge
  ```

**Case 4: Force Push (NGUY HIỂM)**
```bash
git push --force origin feature/my-work
```

**Khi nào dùng:**
- ✅ Branch CÁ NHÂN, chưa ai dùng
- ✅ Đã rebase local branch, cần push
- ❌ KHÔNG ĐƯỢC force push `main` hay `develop`
- ❌ KHÔNG force push branch người khác đang làm

**Tại sao nguy hiểm?** Mất commits của người khác!

**Thực hành:**
```bash
# Scenario: 2 developer
# Developer A:
git clone <repo>
git checkout -b feature/gps
# Code, commit
git push origin feature/gps

# Developer B:
git fetch origin
git checkout feature/gps  # Lấy branch của A
# Review code, test
# Comment trên GitHub/GitLab
```

---

## **LEVEL 3: Nâng Cao (Tuần 5-7)**

### Bài 7: Rebase - Làm Sạch Lịch Sử

**Use Cases:**

**Case 1: Squash Commits - Gộp Nhiều Commits Nhỏ**
```bash
git rebase -i HEAD~5
```

**Scenario:** Bạn code feature GPS module trong 3 ngày:
```
feat: add GPS init
fix typo
fix: correct baud rate
wip: testing
fix: remove debug code
feat: add GPS parsing
oops fix compilation
```

**Vấn đề:** 7 commits rác, reviewer phải đọc hết. Muốn gộp thành 1 commit gọn.

**Giải pháp:**
```bash
git rebase -i HEAD~7

# Editor mở:
pick feat: add GPS init
squash fix typo
squash fix: correct baud rate
squash wip: testing
squash fix: remove debug code
pick feat: add GPS parsing
squash oops fix compilation

# Kết quả: 2 commits sạch
# 1. feat: add GPS init and configuration
# 2. feat: add GPS parsing function
```

**Khi nào dùng:**
- ✅ TRƯỚC KHI push lên remote
- ✅ Branch cá nhân, chưa ai dùng
- ❌ SAU KHI đã push và người khác pull về
- ❌ Trên `main` hoặc shared branches

**Case 2: Edit Commit Message**
```bash
git rebase -i HEAD~3
```

**Scenario:** Commit message sai:
```
fix: update gps.c  ← Không rõ ràng
```

Muốn sửa thành:
```
fix: resolve GPS UART timeout after 30 seconds
```

**Case 3: Reorder Commits**
```bash
git rebase -i HEAD~4
```

**Scenario:** Commits không theo thứ tự logic:
```
1. feat: add web interface
2. docs: update README
3. feat: add GPS module
4. test: add GPS tests
```

Muốn sắp xếp lại:
```
1. feat: add GPS module
2. test: add GPS tests
3. feat: add web interface
4. docs: update README
```

**Case 4: Drop Commits Không Cần**
```bash
git rebase -i HEAD~5
```

**Scenario:** Có commit debug code không muốn đẩy lên production:
```
pick feat: add GPS
pick debug: add printf everywhere  ← Xóa commit này
pick fix: GPS timeout
```

**Case 5: Rebase Branch - Cập Nhật Từ Main**
```bash
git rebase main
```

**Scenario:**
```
main:     A -- B -- C -- D
                \
feature:         X -- Y -- Z
```

Muốn lấy commits mới (C, D) từ `main`:

```bash
git checkout feature/gps
git rebase main

# Kết quả:
main:     A -- B -- C -- D
                           \
feature:                    X' -- Y' -- Z'
```

**Tại sao không merge?**
- Merge: Tạo merge commit, history rối
- Rebase: History thẳng, sạch, dễ đọc

**Khi nào dùng rebase thay vì merge:**
- ✅ Branch cá nhân
- ✅ Muốn history sạch
- ❌ Branch đã share với team → dùng merge

**Thực hành:**
```bash
# Scenario thực tế
# Tạo 5 commits rác
git commit -m "wip"
git commit -m "fix"
git commit -m "update"
git commit -m "asdf"
git commit -m "feat: GPS done"

# Squash thành 1 commit
git rebase -i HEAD~5
# Chọn squash tất cả vào commit đầu
# Viết lại message: "feat: implement GPS coordinate parsing"
```

---

### Bài 8: Git Stash - Lưu Công Việc Dở Dang

**Use Cases:**

**Case 1: Emergency Switch Branch**
```bash
git stash
```

**Scenario:** Bạn đang code GPS module (50% xong), chưa thể commit vì code chưa chạy được. Đột nhiên sếp gọi: "Bug production, fix GẤP!"

```bash
# Đang có 10 files thay đổi, uncommitted
git stash save "WIP: GPS parsing half done"
git checkout main
git checkout -b hotfix/urgent-bug
# Fix bug
git commit
git push

# Quay lại công việc cũ
git checkout feature/gps
git stash pop
# Tiếp tục code
```

**Case 2: Pull Code Mới Nhưng Có Local Changes**
```bash
git stash
git pull
git stash pop
```

**Scenario:** Team push code mới lên `develop`. Bạn muốn pull về nhưng đang có local changes chưa commit.

**Lỗi khi pull:**
```
error: Your local changes to the following files would be overwritten by merge:
        src/gps.c
```

**Giải pháp:**
```bash
git stash           # Cất changes đi
git pull            # Pull code mới
git stash pop       # Lấy changes ra
# Giải quyết conflicts nếu có
```

**Case 3: Test Nhanh Một Idea**
```bash
git stash
# Test idea mới
git stash pop  # Quay lại nếu idea không tốt
```

**Scenario:** Đang code GPS module, nghĩ ra cách tối ưu hơn. Muốn thử nhưng không chắc có tốt hơn.

```bash
git stash           # Lưu code hiện tại
# Code theo cách mới, test
# Nếu không tốt:
git reset --hard
git stash pop       # Lấy code cũ ra
```

**Case 4: Stash Một Phần (Partial Stash)**
```bash
git stash -p
```

**Scenario:** Sửa 2 files: `gps.c` (feature mới) và `main.c` (debug code). Muốn stash debug code, giữ lại feature code.

```bash
git stash -p
# Git hỏi từng thay đổi:
Stash this hunk [y,n,q,a,d,e,?]? 
# y: stash
# n: không stash
```

**Case 5: Multiple Stashes**
```bash
git stash list
git stash apply stash@{1}
```

**Scenario:** Có nhiều công việc dở:
```bash
git stash save "GPS module 50%"
# Switch task
git stash save "Web interface 30%"
# Switch task
git stash save "NTP sync debugging"

# Xem danh sách
git stash list
# stash@{0}: NTP sync debugging
# stash@{1}: Web interface 30%
# stash@{2}: GPS module 50%

# Lấy stash cụ thể
git stash apply stash@{2}  # Lấy GPS module
```

**`stash pop` vs `stash apply`:**
- **`pop`**: Lấy stash ra VÀ xóa khỏi stash list
- **`apply`**: Lấy stash ra NHƯNG giữ trong stash list (backup)

**Case 6: Tạo Branch Từ Stash**
```bash
git stash branch feature/new-gps stash@{0}
```

**Scenario:** Stash quá lâu, quên mất. Muốn biến stash thành branch để code tiếp.

**Thực hành:**
```bash
# Scenario thực tế
# Đang code GPS
vim gps.c  # Sửa code
git stash save "GPS: add coordinate validation"

# Emergency fix
git checkout main
# Fix, commit, push

# Quay lại
git checkout feature/gps
git stash list
git stash pop

# Nếu conflict:
# Giải quyết conflict
git add .
git stash drop  # Xóa stash đã apply
```

---

### Bài 9: Reset, Revert và Undo - Hồi Phục Sai Lầm

**Use Cases:**

**Case 1: `git reset --soft HEAD~1` - Undo Commit, Giữ Changes**

**Scenario:** Vừa commit, phát hiện quên thêm file:
```bash
git commit -m "feat: add GPS module"
# Ối, quên thêm gps.h

git reset --soft HEAD~1
# Giờ gps.c vẫn staged, thêm gps.h vào
git add gps.h
git commit -m "feat: add GPS module"
```

**Khi nào dùng:**
- ✅ Commit message sai → reset, commit lại
- ✅ Quên thêm file vào commit
- ✅ Muốn chia 1 commit lớn thành nhiều commits nhỏ

**Case 2: `git reset --mixed HEAD~1` (default) - Undo Commit + Unstage**

**Scenario:** Commit nhầm code debug:
```bash
git commit -m "feat: GPS parsing"
# Nhưng commit có cả printf() debug code

git reset HEAD~1
# Files vẫn thay đổi nhưng unstaged
# Xóa debug code
vim gps.c
git add gps.c
git commit -m "feat: GPS parsing"
```

**Case 3: `git reset --hard HEAD~1` - Xóa Commit + Xóa Changes (NGUY HIỂM)**

**Scenario:** Commit sai hoàn toàn, muốn xóa bỏ:
```bash
git commit -m "experimental GPS approach"
# Test xong, cách này không tốt, xóa luôn

git reset --hard HEAD~1
# MẤT HẾT code, về commit trước
```

**⚠️ CẢNH BÁO:** Chỉ dùng khi CHẮC CHẮN muốn xóa code!

**Case 4: `git revert` - Undo Commit An Toàn (Không Xóa History)**

**Scenario:** Đã push commit lên remote, phát hiện có bug:
```bash
git log
# commit abc123: feat: new GPS algorithm
# commit def456: fix: UART timeout
# commit ghi789: feat: web interface

# GPS algorithm có bug, muốn undo
# KHÔNG ĐƯỢC dùng reset vì đã push!

git revert abc123
# Tạo commit mới đảo ngược thay đổi của abc123
```

**`reset` vs `revert`:**
- **`reset`**: Xóa commits khỏi history (nguy hiểm nếu đã push)
- **`revert`**: Tạo commit mới để undo (an toàn, giữ nguyên history)

**Khi nào dùng:**
- ✅ `revert`: Commit đã push, team đã pull
- ✅ `reset`: Commit chưa push, local only

**Case 5: `git reset HEAD <file>` - Unstage File**

**Scenario:** Staged nhầm file:
```bash
git add .
# Ối, add cả passwords.txt

git reset HEAD passwords.txt
# Bỏ passwords.txt ra khỏi staging area
```

**Case 6: `git checkout -- <file>` - Undo Working Changes**

**Scenario:** Sửa file, nhưng sửa hỏng:
```bash
vim gps.c
# Sửa loạn xạ, code không chạy

git checkout -- gps.c
# Quay về version cuối cùng đã commit
```

**⚠️ CẢNH BÁO:** Mất HẾT thay đổi chưa commit!

**Case 7: `git reset --hard origin/main` - Sync Với Remote**

**Scenario:** Local code rối hết, muốn sync 100% với remote:
```bash
git reset --hard origin/main
# Xóa HẾT local changes, lấy code từ remote
```

**Khi nào dùng:**
- ✅ Local mess up hoàn toàn
- ✅ Muốn bắt đầu lại từ đầu
- ❌ Có code quan trọng chưa commit → backup trước!

**Case 8: `git clean -fd` - Xóa Untracked Files**

**Scenario:** Tạo nhiều file test, giờ muốn xóa sạch:
```bash
# Có nhiều file *.test, *.tmp
git clean -n   # Preview xem sẽ xóa gì
git clean -fd  # Xóa files và directories
```

**Thực hành Scenarios:**

```bash
# Scenario 1: Commit message sai
git commit -m "update"
git reset --soft HEAD~1
git commit -m "feat: add GPS coordinate validation"

# Scenario 2: Commit nhầm debug code
git commit -a -m "GPS feature"
git reset HEAD~1
vim gps.c  # Xóa debug printf()
git add gps.c
git commit -m "feat: implement GPS parsing"

# Scenario 3: Push rồi mới phát hiện bug
git revert HEAD
git push

# Scenario 4: Local mess up
git reset --hard origin/main
```

---

Bạn muốn tôi tiếp tục chi tiết hóa các Level 4-5 với use cases không? Hoặc muốn tôi tạo cheatsheet tóm tắt "Khi nào dùng lệnh nào"?
