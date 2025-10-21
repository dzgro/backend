# users - Structure

## Overview
- **Collection**: `users`
- **Document Count**: 2
- **Average Document Size**: 246 bytes
- **Total Size**: 492 bytes

## Fields

### `_id`

- **Type**: `str`
- **Sample Values**: `f1b3bd5a-b0e1-701d-49b9-fa2ba91b1bce`, `7153fdea-f0b1-7030-1d97-31e39e100b22`

### `customerid`

- **Type**: `str`
- **Sample Values**: `cust_QFMHWNNYkSH046`, `cust_RRHtf75gvDNLw0`

### `email`

- **Type**: `str`
- **Sample Values**: `dzgrotechnologies@gmail.com`, `kshitiz1701@gmail.com`

### `name`

- **Type**: `str`
- **Sample Values**: `kshitiz sharma`, `kshitiz sharma`

### `phone_number`

- **Type**: `str`
- **Sample Values**: `+919619173661`, `+919619173661`

### `status`

- **Type**: `str`
- **Enum Values**: `Paid`, `Pending Onboarding`

### `temp_account_request`

- **Type**: `dict`

### `temp_account_request.countrycode`

- **Type**: `str`
- **Sample Values**: `MX`

### `temp_account_request.name`

- **Type**: `str`
- **Sample Values**: `mn nm n `

### `temp_account_request.state`

- **Type**: `str`
- **Sample Values**: `AWXPBR`


## Sample Documents

### Sample 1

```json
{
  "_id": "f1b3bd5a-b0e1-701d-49b9-fa2ba91b1bce",
  "email": "dzgrotechnologies@gmail.com",
  "name": "kshitiz sharma",
  "phone_number": "+919619173661",
  "status": "Paid",
  "customerid": "cust_QFMHWNNYkSH046"
}
```

### Sample 2

```json
{
  "_id": "7153fdea-f0b1-7030-1d97-31e39e100b22",
  "email": "kshitiz1701@gmail.com",
  "name": "kshitiz sharma",
  "phone_number": "+919619173661",
  "status": "Pending Onboarding",
  "customerid": "cust_RRHtf75gvDNLw0",
  "temp_account_request": {
    "countrycode": "MX",
    "name": "mn nm n ",
    "state": "AWXPBR"
  }
}
```

