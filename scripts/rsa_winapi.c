#include <common.h>
#include <rsa.h>

void rsa_genkeypair(DATA_BLOB** priv, DATA_BLOB** pub) {
	DWORD dwFlags = 0;
	HCRYPTPROV hProv = (HCRYPTPROV)NULL;
	HCRYPTKEY hKeys = (HCRYPTKEY)NULL;
	DWORD dwDataLen;

	if (!CryptAcquireContext(&hProv, NULL, MS_DEF_PROV, PROV_RSA_FULL, dwFlags))
		CryptAcquireContext(&hProv, NULL, MS_DEF_PROV, PROV_RSA_FULL, CRYPT_NEWKEYSET);
	CryptGenKey(hProv, CALG_RSA_KEYX, CALG_RSA_KEYSIZE | CRYPT_EXPORTABLE,
			&hKeys);
	CryptExportKey(hKeys, (HCRYPTKEY)NULL, PUBLICKEYBLOB, 0, NULL,
			&dwDataLen);
	*pub = createDataBlob(dwDataLen);
	CryptExportKey(hKeys, (HCRYPTKEY)NULL, PUBLICKEYBLOB, 0, (*pub)->pbData,
			&(*pub)->cbData);
	CryptExportKey(hKeys, (HCRYPTKEY)NULL, PRIVATEKEYBLOB, 0, NULL,
			&dwDataLen);
	*priv = createDataBlob(dwDataLen);
	CryptExportKey(hKeys, (HCRYPTKEY)NULL, PRIVATEKEYBLOB, 0, (*priv)->pbData,
			&(*priv)->cbData);

	CryptDestroyKey(hKeys);
	CryptReleaseContext(hProv, 0);
}

DATA_BLOB* rsa_encrypt(DATA_BLOB* in, DATA_BLOB* pub){
	DATA_BLOB* out = 0,  *buffer = 0;
	DWORD dwFlags = 0;
	HCRYPTPROV hProv = (HCRYPTPROV)NULL;
	HCRYPTKEY hPubKey = (HCRYPTKEY)NULL;
	DWORD dwDataLen, dwBlockLen, dwBlockSize;
	DWORD totalRead = 0, totalWritten = 0;

	if (!CryptAcquireContext(&hProv, NULL, MS_DEF_PROV, PROV_RSA_FULL, dwFlags))
			CryptAcquireContext(&hProv, NULL, MS_DEF_PROV, PROV_RSA_FULL, CRYPT_NEWKEYSET);
	CryptImportKey(hProv,pub->pbData, pub->cbData, 0, CRYPT_EXPORTABLE, &hPubKey);

	dwDataLen=sizeof(dwBlockLen);
    CryptGetKeyParam(hPubKey, KP_BLOCKLEN, (LPBYTE)&dwBlockLen,&dwDataLen,0);
    dwBlockSize = dwBlockLen/8;

    buffer = createDataBlob(dwBlockSize);
    out = createDataBlob((in->cbData / dwBlockSize + 1)*dwBlockSize);

	if (in->cbData > CALG_RSA_BLOCKSIZE){
		while (totalRead <= in->cbData-CALG_RSA_BLOCKSIZE){
			memcpy(buffer->pbData, in->pbData+totalRead, CALG_RSA_BLOCKSIZE);
			buffer->cbData = CALG_RSA_BLOCKSIZE;
			CryptEncrypt(hPubKey, 0, 0, 0, buffer->pbData, &buffer->cbData, CALG_RSA_BLOCKSIZE);
			memcpy(out->pbData + totalWritten, buffer->pbData, buffer->cbData);
			totalRead += CALG_RSA_BLOCKSIZE;
			totalWritten += buffer->cbData;
		}
	}
	if (totalRead < in->cbData){
		memcpy(buffer->pbData, in->pbData+totalRead, in->cbData-totalRead);
		buffer->cbData = in->cbData-totalRead;
		CryptEncrypt(hPubKey, 0, 1, 0, buffer->pbData, &buffer->cbData, CALG_RSA_BLOCKSIZE);
		memcpy(out->pbData + totalWritten, buffer->pbData, buffer->cbData);
		totalRead = in->cbData;
		totalWritten += buffer->cbData;
	}
	out->cbData = totalWritten;

    freeDataBlob(buffer);
    CryptDestroyKey(hPubKey);
    CryptReleaseContext(hProv,0);

	return out;
}

DATA_BLOB* rsa_decrypt(DATA_BLOB* in, DATA_BLOB* priv){
	DATA_BLOB* out = 0,  *buffer = 0;
	DWORD dwFlags = 0;
	HCRYPTPROV hProv = (HCRYPTPROV)NULL;
	HCRYPTKEY hPrivKey = (HCRYPTKEY)NULL;
	DWORD dwDataLen, dwBlockLen, dwBlockSize;
	DWORD totalRead = 0, totalWritten = 0;

	if (!CryptAcquireContext(&hProv, NULL, MS_DEF_PROV, PROV_RSA_FULL, dwFlags))
			CryptAcquireContext(&hProv, NULL, MS_DEF_PROV, PROV_RSA_FULL, CRYPT_NEWKEYSET);
	CryptImportKey(hProv,priv->pbData, priv->cbData, 0, CRYPT_EXPORTABLE, &hPrivKey);

	dwDataLen=sizeof(dwBlockLen);
    CryptGetKeyParam(hPrivKey, KP_BLOCKLEN, (LPBYTE)&dwBlockLen,&dwDataLen,0);
    dwBlockSize = dwBlockLen/8;

    buffer = createDataBlob(dwBlockSize);
    out = createDataBlob((in->cbData / dwBlockSize + 1)*dwBlockSize);

	if (in->cbData > CALG_RSA_BLOCKSIZE){
		while (totalRead <= in->cbData-CALG_RSA_BLOCKSIZE){
			memcpy(buffer->pbData, in->pbData+totalRead, CALG_RSA_BLOCKSIZE);
			buffer->cbData = CALG_RSA_BLOCKSIZE;
			CryptDecrypt(hPrivKey, 0, 0, 0, buffer->pbData, &buffer->cbData);
			memcpy(out->pbData + totalWritten, buffer->pbData, buffer->cbData);
			totalRead += CALG_RSA_BLOCKSIZE;
			totalWritten += buffer->cbData;
		}
	}
	if (totalRead < in->cbData){
		memcpy(buffer->pbData, in->pbData+totalRead, in->cbData-totalRead);
		buffer->cbData = in->cbData-totalRead;
		CryptDecrypt(hPrivKey, 0, 1, 0, buffer->pbData, &buffer->cbData);
		memcpy(out->pbData + totalWritten, buffer->pbData, buffer->cbData);
		totalRead = in->cbData;
		totalWritten += buffer->cbData;
	}
	out->cbData = totalWritten;

    freeDataBlob(buffer);
    CryptDestroyKey(hPrivKey);
    CryptReleaseContext(hProv,0);

	return out;
}

