`skills.md` thường là **một file Markdown** dùng như “sổ tay kỹ năng / playbook” cho LLM khi làm việc coding trong một repo. Ý tưởng là: thay vì mỗi lần lại phải nhắc LLM “hãy viết test, hãy theo style này, dùng tool kia…”, đội ngũ sẽ **chuẩn hoá** thành một tài liệu cố định để LLM đọc và làm theo.

Nó có thể được gọi bằng nhiều tên: `skills.md`, `AI_GUIDE.md`, `CONTRIBUTING.md` (phần dành cho AI), `PROMPT.md`, v.v. Nhưng mục tiêu giống nhau: **đưa luật chơi + workflow + tiêu chuẩn** vào một chỗ.

## Thường `skills.md` chứa gì?

* **Cách setup môi trường**: cài deps, chạy app, chạy test, lint.
* **Coding conventions**: naming, formatting, kiến trúc (DDD/Clean), error handling.
* **Testing rules**: ưu tiên unit/integration, mock thế nào, coverage tối thiểu.
* **Git workflow**: branch naming, commit message, PR checklist.
* **Patterns “nên dùng / tránh dùng”**: ví dụ không dùng singleton, không hardcode secrets, không viết query N+1…
* **Definition of Done**: code + test + docs + typecheck + benchmark (nếu có).
* **Cách làm việc với LLM**: cách yêu cầu, cách cung cấp context, cách trả lời (ngắn/gọn, có patch/diff, có lệnh chạy).

## Ví dụ một `skills.md` (mẫu rút gọn)

Dưới đây là ví dụ kiểu “repo backend Node/TS”:

```md
# skills.md — Engineering Playbook for AI + Humans

## 1) Commands
- Install: `pnpm i`
- Dev: `pnpm dev`
- Test: `pnpm test`
- Lint: `pnpm lint`
- Typecheck: `pnpm typecheck`

## 2) Code style
- TypeScript strict mode, no `any` unless justified.
- Prefer pure functions; avoid hidden side effects.
- Use `zod` for request validation.
- Errors: throw domain errors; map to HTTP in controller layer.

## 3) Architecture
- `src/domain`: business logic (no DB / no HTTP)
- `src/infra`: DB, queues, external APIs
- `src/api`: controllers/routes
Rule: domain must not import from infra/api.

## 4) Testing
- Every bugfix must include a regression test.
- Prefer integration tests for DB queries.
- Use factories in `test/factories`.

## 5) PR checklist
- [ ] Tests added + passing
- [ ] No new eslint/type errors
- [ ] Logs have no PII
- [ ] Updated docs if behavior changes
```

## Ví dụ “LLM dùng skills.md” trong thực tế

Giả sử bạn yêu cầu:

> “Hãy thêm endpoint `POST /users` tạo user mới, validate email, và viết test.”

Một LLM “đọc skills.md” sẽ tự động:

* dùng `zod` để validate body (vì rules nói vậy),
* đặt logic tạo user vào `src/domain`,
* mapping HTTP ở `src/api`,
* thêm integration test theo hướng dẫn,
* nhắc bạn chạy `pnpm test`, `pnpm lint`, `pnpm typecheck`.

## Bạn muốn ví dụ sát với repo của bạn hơn?

Nếu bạn nói bạn dùng stack nào (Python/FastAPI, Java/Spring, Go, Node/TS…) mình có thể viết một bản `skills.md` “chuẩn đội” cho stack đó (ngắn ~1 trang) để copy vào repo dùng luôn.


Dưới đây là 2 “skills” kiểu `skills.md` bạn có thể copy vào repo: **(1) Refactor tối ưu** và **(2) Check lỗi** cho dự án **STM32G474 + HAL + Keil C (MDK-ARM)**. Mình viết theo hướng “LLM đọc vào là làm được ngay”, có checklist + pattern cụ thể.

---

## 1) skill_refactor_optimize.md (Refactor tối ưu)

```md
# Skill: Refactor & Optimize (STM32G474 + HAL + KeilC)

## Mục tiêu
- Giữ nguyên hành vi (no functional regression).
- Giảm độ phức tạp, tăng readability, giảm bug tiềm ẩn.
- Tối ưu runtime theo hướng embedded (CPU/RAM/latency), nhưng ưu tiên correctness.

## Nguyên tắc refactor
1) Không sửa nhiều thứ cùng lúc: mỗi commit/patch chỉ 1 mục tiêu.
2) Không đổi API public nếu không bắt buộc.
3) Không tối ưu “mù”: chỉ tối ưu khi có dấu hiệu bottleneck (ISR trễ, jitter, stack cao, DMA underrun/overrun).
4) Ưu tiên deterministic time: tránh malloc/free, tránh vòng lặp không giới hạn.

## Cấu trúc code đề xuất
- app/: logic ứng dụng (state machine, control loop)
- drivers/: wrapper cho HAL (uart.c, adc.c, pwm.c) -> cung cấp API gọn, ít HAL leak
- bsp/: board-specific (pin map, enable peripheral, power)
- middleware/: ring buffer, fifo, filters, math utils
- diag/: assert, fault log, error counters

## Refactor patterns nên dùng
### A) "HAL wrapper" để giảm coupling
- Không gọi HAL trực tiếp ở mọi nơi.
- Tạo module driver có API ổn định:
  - uart_write(), uart_read(), adc_start_dma(), pwm_set_duty()
- Mọi callback HAL (HAL_UART_RxCpltCallback…) chỉ forward event vào app layer.

### B) State machine thay vì if/else dài
- Tạo enum state + hàm step():
  - app_step_1ms(), app_step_10ms()
- ISR không làm nặng: ISR chỉ set flag / push event.

### C) Tách ISR khỏi xử lý nặng (defer work)
- ISR chỉ:
  - đọc register tối thiểu
  - clear flag
  - push vào queue / set bit
- Xử lý nặng chạy ở main loop hoặc task tick.

### D) DMA/Timer-driven thay vì polling
- ADC: ưu tiên DMA circular + half/full callback.
- UART RX: ưu tiên idle line + DMA (nếu phù hợp) hoặc interrupt + ring buffer.
- PWM/Control loop: dùng timer update interrupt/tick.

### E) Tối ưu memory/time kiểu embedded
- Tránh float nếu không cần; nếu cần thì dùng `float` (STM32G4 có FPU single-precision).
- Hạn chế printf trong runtime; dùng macro log có mức độ (compile-time enable).
- Ring buffer cố định; không dùng malloc.

## Checklist refactor (LLM phải làm)
- [ ] Liệt kê "behavior invariants" trước khi sửa (input/output, timing, units).
- [ ] Xác định phạm vi: file nào, function nào, phụ thuộc nào.
- [ ] Tạo patch nhỏ, compile được sau mỗi bước.
- [ ] Không thay đổi thứ tự init clocks/peripherals trừ khi có lý do rõ ràng.
- [ ] Với code chạy ISR: đảm bảo O(1) và không gọi hàm blocking.
- [ ] Không gọi HAL_Delay trong ngữ cảnh ISR.
- [ ] Kiểm tra stack usage (ưu tiên tránh local buffer lớn trong ISR).
- [ ] Update comment/README nếu thay đổi kiến trúc.

## Các “điểm nóng” hay cần refactor trong HAL project
- Callback HAL quá nhiều logic -> move to app event queue.
- UART RX bị mất byte -> ring buffer + xử lý idle line.
- ADC sampling jitter -> timer trigger ADC + DMA.
- Control loop trộn lẫn init/config -> tách config khỏi run-time.

## Cách chứng minh refactor không làm sai
- Build ở Keil: 0 error, 0 warning (hoặc warning đã được justify).
- Test tối thiểu:
  - chạy trên board: UART echo / ADC waveform / PWM output đúng.
  - nếu có: bật pin debug đo ISR latency bằng oscilloscope/LA.
- Thêm "self-check" runtime (counter, checksum frame, range check).
```

---

## 2) skill_error_check.md (Skill check lỗi / bắt bug)

```md
# Skill: Error Checking & Fault Handling (STM32G474 + HAL + KeilC)

## Mục tiêu
- Bắt lỗi sớm (compile-time + runtime).
- Có đường đi rõ ràng khi lỗi xảy ra: log + safe state + khả năng chẩn đoán.
- Tránh hardfault “im lặng”.

## 1) Compile-time checks (bắt lỗi khi build)
### A) Bật warning mức cao trong Keil
- Arm Compiler 6: bật warning đầy đủ, treat warnings as errors nếu được.
- Tắt các warning rác bằng cách sửa code, không “disable hàng loạt”.

### B) Static assertions
- Dùng `static_assert` (C11) hoặc macro fallback:
  - check size struct, buffer length, enum range.

### C) MISRA-ish rules (thực dụng)
- Không implicit cast nguy hiểm.
- Không dùng magic numbers: define/enum rõ.

## 2) Runtime checks (quan trọng nhất)
### A) ASSERT có hành vi rõ ràng
- `ASSERT(expr)` khi fail phải:
  - lưu file/line (hoặc hash)
  - lưu error code
  - vào safe state (disable outputs / PWM off)
  - không reset ngay nếu cần chẩn đoán (tùy dự án)

### B) HAL error hooks
- Override/implement:
  - `Error_Handler()`
  - `HAL_MspInit` fail paths
  - callbacks error (UART error, ADC error…)
- Khi HAL trả `HAL_ERROR/HAL_TIMEOUT` → convert thành code lỗi nội bộ.

### C) Fault capture (HardFault/BusFault/UsageFault)
- Lưu:
  - stacked PC/LR/xPSR
  - CFSR/HFSR/MMFAR/BFAR
- Ghi vào RAM vùng “noinit” để sau reset đọc lại.

### D) Watchdog strategy
- IWDG chỉ feed ở main loop sau khi:
  - tick OK
  - các module critical OK
- Không feed trong ISR.

## 3) Các lỗi hay gặp trên STM32 + HAL và cách check
### UART
- Overrun / framing -> check `HAL_UART_ErrorCallback`, đọc SR/ISR đúng cách.
- RX lost -> ring buffer + idle line detect.

### ADC + DMA
- DMA overrun/half-transfer xử lý sai -> verify buffer size, alignment, circular mode.
- Sampling jitter -> dùng timer trigger ADC.

### Timer/PWM
- Duty vượt range -> clamp + assert.
- Dead-time config sai (nếu dùng advanced timer) -> validate register.

### Clock/PLL
- Sai clock dẫn đến baud sai -> log SystemCoreClock và validate.

## 4) “Error code” & Diagnostic model
- Mỗi module có error code namespace:
  - ERR_UART_*, ERR_ADC_*, ERR_CTRL_*
- Có counters:
  - error_count, last_error, last_error_tick
- Có API:
  - diag_get_last_fault(), diag_clear()

## 5) Checklist check lỗi (LLM phải làm)
- [ ] Mọi HAL call critical đều check return status.
- [ ] Không bỏ qua timeout/NULL.
- [ ] ISR: không gọi function blocking, không dùng printf.
- [ ] Validate input từ ngoại vi (CRC/range/length).
- [ ] Clamp mọi giá trị điều khiển (PWM duty, current ref…).
- [ ] Bật watchdog theo chiến lược “feed có điều kiện”.
- [ ] Có HardFault capture + cách đọc sau reset.
```

---

Nếu bạn muốn mình “đóng gói” thành một `skills.md` duy nhất cho repo (có thêm skeleton code: `assert.h`, `fault_dump.c`, `ring_buffer.c`, mẫu `Error_Handler()` + HardFault handler), bạn gửi cho mình:

* bạn dùng **AC6 hay AC5**,
* project có **FreeRTOS** không,
* UART bạn đang dùng kiểu **DMA + idle line** hay **interrupt**.

