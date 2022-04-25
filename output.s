
	.data
$LC0:	.asciiz	"Value of a = "
$LC1:	.asciiz	"\nValue at address stored in b = "
$LC2:	.asciiz	"\nNew Value of a = "
$LC3:	.asciiz	"\nValue at address stored in b = "

	.text
main:
	sw $31, -4($29)                           
	addiu $29, $29, -4
	sw $30, -4($29)                           
	addiu $29, $29, -4
	addu $30, $0, $29
	addiu $29, $29, -16
	li $8, 1
	sw $8, -12($30)
	addiu $9, $30, -12
	lw $10, 0($9)
	sw $10, -8($30)
	la $a0, $LC0
	li $v0, 4
	syscall
	addu $4, $0, $8
	li $v0, 1
	syscall
	la $a0, $LC1
	li $v0, 4
	syscall
	addiu $9, $30, -8
	lw $9, 0($9)
	lw $10, 0($9)
	sw $10, -16($30)
	addu $4, $0, $10
	li $v0, 1
	syscall
	li $9, 2
	sw $9, -12($30)
	la $a0, $LC2
	li $v0, 4
	syscall
	addu $4, $0, $9
	li $v0, 1
	syscall
	addiu $11, $30, -8
	lw $8, 0($11)
	lw $10, 0($8)
	sw $10, -16($30)
	la $a0, $LC3
	li $v0, 4
	syscall
	addu $4, $0, $10
	li $v0, 1
	syscall
	addiu $29, $29, 16
	lw $30, 0($29)                           
	addiu $29, $29, 4
	lw $31, 0($29)                           
	addiu $29, $29, 4
	jr $31