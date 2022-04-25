
	.data
$LC0:	.word	1066192076
$LC1:	.word	1056964608
$LC2:	.word	1069547520

	.text
main:
	sw $31, -4($29)                           
	addiu $29, $29, -4
	sw $30, -4($29)                           
	addiu $29, $29, -4
	addu $30, $0, $29
	addiu $29, $29, -16
	lwc1 $f0, $LC0
	swc1 $f0, -4($30)
	lwc1 $f1, $LC1
	swc1 $f1, -8($30)
	lwc1 $f2, $LC2
	swc1 $f2, -12($30)
	add.s $f0, $f0, $f2
	div.s $f0, $f0, $f1
	swc1 $f0, -16($30)
	mov.s $f12, $f0
	li $v0, 2
	syscall
	addiu $29, $29, 16
	lw $30, 0($29)                           
	addiu $29, $29, 4
	lw $31, 0($29)                           
	addiu $29, $29, 4
	jr $31