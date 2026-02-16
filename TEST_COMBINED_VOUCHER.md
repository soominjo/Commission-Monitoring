# Combined Voucher Fix - Quick Test Guide

## Test Setup

### Prerequisites
1. Have at least one TrancheRecord with multiple pending tranches
2. Be logged in as superuser or staff
3. Have the server running

## Quick Test Steps

### Step 1: Before Generating Combined Voucher
1. Navigate to: `/sparc/tranche/edit/{tranche_id}/`
2. Note the current state of tranches:
   ```
   Tranche #1: Status = "Pending", Received = ₱0
   Tranche #2: Status = "Pending", Received = ₱0
   Tranche #3: Status = "Pending", Received = ₱0
   ```

### Step 2: Generate Combined Voucher
1. Check checkboxes for Tranches #1, #2, #3
2. Observe the summary updates:
   ```
   3 tranches selected • Total Expected Commission: ₱ 30,000.00
   ```
3. Click **"Generate Voucher"** button
4. Should see success message:
   ```
   ✅ Combined voucher created successfully! 3 tranche(s) linked to voucher COMBINED-DP-{id}-1-2-3. Total: ₱30,000.00
   ```

### Step 3: Verify in edit_tranche.html
1. Page should reload and show:
   ```
   Tranche #1: Status = "Received" ✅, Received = ₱10,000, Checkbox disabled
   Tranche #2: Status = "Received" ✅, Received = ₱10,000, Checkbox disabled
   Tranche #3: Status = "Received" ✅, Received = ₱10,000, Checkbox disabled
   ```
2. Each should have purple "Combined" badge

### Step 4: Verify in view_tranche.html
1. Navigate to: `/sparc/tranche/{tranche_id}/`
2. Check Down Payment Schedule table:
   ```
   Tranche | Status      | Actual Comm | Date Received | Voucher
   --------|-------------|-------------|---------------|--------
   1       | Received ✅  | ₱10,000    | Today         | 🟣 Combined
   2       | Received ✅  | ₱10,000    | Today         | 🟣 Combined
   3       | Received ✅  | ₱10,000    | Today         | 🟣 Combined
   ```

### Step 5: Verify in tranche_history.html
1. Navigate to: `/sparc/tranche_history/`
2. Find the tranche record card
3. Check progress:
   ```
   Progress: 3/10 ✅
   Status: In Progress (was: Pending) ✅
   Progress bar: 30% (was: 0%) ✅
   ```

### Step 6: Verify in receivables.html
1. Navigate to: `/sparc/receivables/`
2. Find the commission record:
   ```
   Release Number: COMBINED-DP-{record_id}-1-2-3
   Amount: ₱30,000.00
   Date Released: Today
   Type: Combined Tranche Payment (3 tranches)
   ```

## What to Look For

### ✅ Success Indicators
- [x] Tranches show "Received" status (green badge)
- [x] Actual commission amounts are filled in (not ₱0)
- [x] Date received is today's date
- [x] Purple "Combined" badge appears
- [x] Checkboxes are disabled for combined tranches
- [x] Progress bars update in tranche_history
- [x] Commission record appears in receivables

### ❌ Failure Indicators
- [ ] Tranches still show "Pending" status
- [ ] Received amounts are still ₱0
- [ ] Date received is blank
- [ ] No "Combined" badge appears
- [ ] Progress bars don't update
- [ ] Commission record missing in receivables

## Database Verification (Optional)

If you have database access, check TranchePayment records:

```sql
-- Check the updated tranches
SELECT 
    id,
    tranche_number,
    status,
    received_amount,
    date_received,
    combined_voucher_number
FROM sparc_tranchepayment
WHERE tranche_record_id = {your_record_id}
    AND tranche_number IN (1, 2, 3);
```

**Expected Results:**
```
id  | tranche_number | status   | received_amount | date_received | combined_voucher_number
----|----------------|----------|-----------------|---------------|------------------------
1   | 1              | Received | 10000.00        | 2024-10-26    | COMBINED-DP-X-1-2-3
2   | 2              | Received | 10000.00        | 2024-10-26    | COMBINED-DP-X-1-2-3
3   | 3              | Received | 10000.00        | 2024-10-26    | COMBINED-DP-X-1-2-3
```

## Troubleshooting

### Issue: Tranches still show as "Pending"
**Check:**
1. Verify you clicked "Generate Voucher" (not "Save All Changes")
2. Check browser console for JavaScript errors
3. Check Django logs for save errors
4. Verify tranches weren't already in another combined voucher

### Issue: Amounts are incorrect
**Check:**
1. Verify the commission calculation logic in view_tranche matches
2. Check if Net of VAT divisor is set correctly
3. Verify tax rates and percentages are configured properly

### Issue: No "Combined" badge appears
**Check:**
1. Verify `combined_voucher_number` field was saved
2. Check if template is rendering the badge correctly
3. Refresh the page to ensure latest data is loaded

## Edge Case Tests

### Test A: Mixed DP and LTO
1. Select 2 DP tranches and 1 LTO tranche
2. Generate combined voucher
3. Verify LTO uses different calculation (option2_value)

### Test B: Single Tranche
1. Select only 1 tranche
2. Should still work (validation allows >= 1)
3. Verify release number format: COMBINED-DP-{id}-{tranche_num}

### Test C: Already Combined
1. Try to check tranches that are already in a voucher
2. Checkboxes should be disabled
3. Tooltip should explain they're already combined

## Log Monitoring

Watch the Django logs for these entries:

```
INFO - Created combined voucher for {agent_name}: COMBINED-DP-{id}-{nums} - ₱{amount}
INFO - Linked tranche #{num} to combined voucher COMBINED-DP-{id}-{nums} with amount ₱{amount}
```

Each selected tranche should have its own "Linked tranche" log entry.

## Success Confirmation

✅ **The fix is working correctly if:**
1. All 6 test steps pass
2. Success indicators are all checked
3. No failure indicators appear
4. Database shows correct values (if checked)
5. Logs show proper linking messages

---

**Test Date**: _____________
**Tested By**: _____________
**Result**: ⬜ Pass  ⬜ Fail
**Notes**: _____________________________________________
